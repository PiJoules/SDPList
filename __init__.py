# Call vendor to add the dependencies to the classpath
import vendor
vendor.add('lib')

import pymongo

# Import the Flask Framework
from flask import Flask, render_template
app = Flask(__name__)


# Create mongoconnection
from private.MongoClientConnection import MongoClientConnection
client = MongoClientConnection().connection.SDP

# Root directory
@app.route("/")
def index():
	projects = list(client.projects.find(limit=5))
	students = list(client.students.find(limit=4))
	advisers = list(client.advisers.find(limit=4))
	return render_template("index.html", projects=projects, students=students, advisers=advisers)

@app.route("/signup/")
def signup():
	return render_template("signup.html")

if __name__ == '__main__':
    app.run()

