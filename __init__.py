# Call vendor to add the dependencies to the classpath
import vendor
vendor.add('lib')

from datetime import datetime
import re
import math
import pymongo
from flask_oauthlib.client import OAuth
from bson.objectid import ObjectId

# Import the Flask Framework
from flask import Flask, render_template, redirect, url_for, session, request, jsonify, abort
app = Flask(__name__)
oauth = OAuth(app)


# Create mongoconnection
from private.MongoClientConnection import MongoClientConnection
client = MongoClientConnection().connection.SDP

from private.Authentication import Authentication
authentication = Authentication()
app.secret_key = authentication.secret_key

linkedin = oauth.remote_app(
    'linkedin',
    consumer_key=authentication.linkedin_client_id,
    consumer_secret=authentication.linkedin_client_secret,
    request_token_params={
        'scope': ['r_basicprofile', 'r_emailaddress'],
        'state': 'RandomString',
    },
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)

page_count = 5 # Amount to display per page on search results
paginate_count = 5 # Number of paginate indecies to display

# Root directory
@app.route("/")
def index():
	projects = list(client.projects.find(limit=5))
	students = list(client.people.find({
		"type": "student",
		"major": {"$exists": True, "$ne": ""},
		"interests": {"$exists": True, "$ne": [""]}
	}, limit=4, sort=[("joined", -1)]))
	advisers = list(client.people.find({
		"type": "adviser",
		"major": {"$exists": True, "$ne": ""},
		"interests": {"$exists": True, "$ne": [""]}
	}, limit=4, sort=[("joined", -1)]))
	return render_template("index.html",
		projects=projects,
		students=students, 
		advisers=advisers, 
		signed_in=is_signed_in()
	)

@app.route("/account/")
def account():
	if not is_signed_in():
		return redirect("/signup/")

	person = client.people.find_one({"email": session["email"]})
	return render_template("settings.html",
		signed_in=is_signed_in(),
		person=person
	)

@app.route("/add_project", methods=["GET", "POST"])
def add_project():
	if request.method == "POST":
		project = request.form # this is an ImmutableMultiDict, not a dict
		next_project = {
			"team": []
		}
		for key in project:
			val = project[key]
			if key == "":
				return "Missing parameters"
			next_project[key] = val
		client.projects.insert(next_project)
		return "success"
	else:
		if not is_signed_in():
			return redirect("/signup/")

		return render_template("add_project.html",
			signed_in=is_signed_in()
		)

@app.route("/user/<user_id>/")
def profile(user_id):
	if not ObjectId.is_valid(user_id):
		abort(404)

	objID = ObjectId(user_id)
	if client.people.find({"_id": objID}, limit=1).count(with_limit_and_skip=True) <= 0:
		abort(404)

	person = client.people.find_one({"_id": objID})
	return render_template("wall.html",
		signed_in=is_signed_in(),
		person=person
	)

@app.route("/project/<project_id>/")
def project(project_id):
	if not ObjectId.is_valid(project_id):
		abort(404)

	objID = ObjectId(project_id)
	if client.projects.find({"_id": objID}, limit=1).count(with_limit_and_skip=True) <= 0:
		abort(404)

	project = client.projects.find_one({"_id": objID})
	return render_template("project.html",
		signed_in=is_signed_in(),
		project=project
	)

@app.route("/search/")
@app.route("/search/page/<num>/")
def search(num=1):
	num = int(num)-1
	if num < 0:
		num = 0

	query = request.args.get("q")
	category = request.args.get("c")
	if not category:
		category = "projects"

	# Search projects
	reg = re.compile(".*" + query + ".*", re.IGNORECASE)
	skip = max(0, (num-int(paginate_count/2))*page_count)
	limit = paginate_count*paginate_count
	if category == "projects":
		results = client.projects.find({"title": reg}, skip=skip, limit=limit)
	elif category == "people":
		results = client.people.find(
			{ "$or": [
				{"fullName": reg},
				{"major": reg}
			]},
			skip=skip,
			limit=limit
		)
	elif category == "students":
		results = client.people.find(
			{
				"$or": [
					{"fullName": reg},
					{"major": reg}
				],
				"type": "student"
			},
			skip=skip,
			limit=limit
		)
	elif category == "advisers":
		results = client.people.find(
			{
				"$or": [
					{"fullName": reg},
					{"major": reg}
				],
				"type": "adviser"
			},
			skip=skip,
			limit=limit
		)
	else:
		# Search projects by default
		results = client.projects.find({"title": reg}, skip=skip, limit=limit)

	results = list(results)
	results_to_display = results[num*page_count:(num+1)*page_count]
	for i in range(len(results_to_display)):
		result = results_to_display[i]
		if category == "projects":
			team = result["team"] # List of ObjIds
			people = list(client.people.find({"_id": {"$in": team}}))
			results_to_display[i]["team"] = people
		else:
			personID = result["_id"]
			projects = list(client.projects.find({"team": personID}))
			results_to_display[i]["projects"] = projects

	first_paginate = max(1, num+1-int(page_count/2))
	last_paginate = min( num+1+int(page_count/2), int(math.ceil(float(skip+len(results))/page_count)) )
	return render_template("search.html",
		signed_in=is_signed_in(),
		query=query,
		results=results_to_display,
		category=category,
		page_num=num+1,
		page_count=page_count,
		first_paginate=first_paginate,
		last_paginate=last_paginate
	)

@app.route("/signup/")
def signup():
	if is_signed_in():
		return redirect("/")
	return render_template("signup.html")

@app.route("/signup/linkedin/")
def signup_linkedin():
	return linkedin.authorize(callback="http://127.0.0.1:5000/auth/linkedin/callback")

@app.route("/update_user", methods=['POST'])
def update_user():
	if not is_signed_in():
		return redirect("/")

	person = request.form # this is an ImmutableMultiDict, not a dict
	updated_person = {}
	for key in person:
		val = person[key]
		if key == "interests":
			updated_person[key] = re.split(',\s*', val)
		else:
			updated_person[key] = val

	client.people.update({"email": session["email"]}, {"$set": updated_person})
	return jsonify(person=updated_person)

@app.route("/auth/linkedin/callback/")
def linkedin_authorize():
    resp = linkedin.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['linkedin_token'] = (resp['access_token'], '')

    # Get as much infromation about the person from basic info and email
    me = linkedin.get("people/~:(id,email-address,first-name,last-name,headline,picture-url,industry,summary,specialties,positions:(id,title,summary,start-date,end-date,is-current,company:(id,name,type,size,industry,ticker)),educations:(id,school-name,field-of-study,start-date,end-date,degree,activities,notes),associations,interests,num-recommenders,date-of-birth,publications:(id,title,publisher:(name),authors:(id,name),date,url,summary),patents:(id,title,summary,number,status:(id,name),office:(name),inventors:(id,name),date,url),languages:(id,language:(name),proficiency:(level,name)),skills:(id,skill:(name)),certifications:(id,name,authority:(name),number,start-date,end-date),courses:(id,name,number),recommendations-received:(id,recommendation-type,recommendation-text,recommender),honors-awards,three-current-positions,three-past-positions,volunteer)")
    data = me.data
    session["email"] = data["emailAddress"]

    # Add new user
    if client.people.find({"email": data["emailAddress"]}, limit=1).count(with_limit_and_skip=True) <= 0:
    	client.people.insert({
    		"email": data["emailAddress"],
    		"firstName": data["firstName"],
    		"lastName": data["lastName"],
    		"type": "student",
    		"joined": datetime.now()
    	})

    return redirect("/")

@app.route("/logout/")
def logout():
	session.pop("email", None)
	session.pop('linkedin_token', None)
	return redirect("/")

@app.errorhandler(404)
def page_not_found(error):
	return render_template('page_not_found.html'), 404

@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get('linkedin_token')

def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

def is_signed_in():
	return "linkedin_token" in session

linkedin.pre_request = change_linkedin_query

if __name__ == '__main__':
    app.run()

