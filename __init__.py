# Call vendor to add the dependencies to the classpath
import vendor
vendor.add('lib')

from datetime import datetime
import pymongo
from flask_oauthlib.client import OAuth

# Import the Flask Framework
from flask import Flask, render_template, redirect, url_for, session, request, jsonify
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

# Root directory
@app.route("/")
def index():
	if "linkedin_token" in session:
		pass
	projects = list(client.projects.find(limit=5))
	students = list(client.people.find({
		"type": "student",
		"major": {"$exists": True},
		"interests": {"$exists": True}
	}, limit=4, sort=[("joined", -1)]))
	advisers = list(client.people.find({
		"type": "adviser",
		"major": {"$exists": True},
		"interests": {"$exists": True}
	}, limit=4, sort=[("joined", -1)]))
	return render_template("index.html",
		projects=projects,
		students=students, 
		advisers=advisers, 
		signed_in="linkedin_token" in session
	)

@app.route("/signup/")
def signup():
	if "linkedin_token" in session:
		return redirect("/")
	return render_template("signup.html")

@app.route("/signup/linkedin/")
def signup_linkedin():
	return linkedin.authorize(callback="http://127.0.0.1:5000/auth/linkedin/callback")

@app.route("/auth/linkedin/callback/")
def linkedin_authorize():
    resp = linkedin.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['linkedin_token'] = (resp['access_token'], '')
    #me = linkedin.get('people/~')
    #my_id = me.data["id"]
    me = linkedin.get("people/~:(id,email-address,first-name,last-name,headline,picture-url,industry,summary,specialties,positions:(id,title,summary,start-date,end-date,is-current,company:(id,name,type,size,industry,ticker)),educations:(id,school-name,field-of-study,start-date,end-date,degree,activities,notes),associations,interests,num-recommenders,date-of-birth,publications:(id,title,publisher:(name),authors:(id,name),date,url,summary),patents:(id,title,summary,number,status:(id,name),office:(name),inventors:(id,name),date,url),languages:(id,language:(name),proficiency:(level,name)),skills:(id,skill:(name)),certifications:(id,name,authority:(name),number,start-date,end-date),courses:(id,name,number),recommendations-received:(id,recommendation-type,recommendation-text,recommender),honors-awards,three-current-positions,three-past-positions,volunteer)")
    #return jsonify(me=me.data)
    data = me.data
    if client.people.find({"email": data["emailAddress"]}).count() <= 0:
    	client.people.insert({
    		"email": data["emailAddress"],
    		"firstName": data["firstName"],
    		"lastName": data["lastName"],
    		"photo": data["pictureUrl"],
    		"joined": datetime.now()
    	})
    return redirect("/")

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

linkedin.pre_request = change_linkedin_query

@app.route("/logout/")
def logout():
    session.pop('linkedin_token', None)
    return redirect("/")

if __name__ == '__main__':
    app.run()

