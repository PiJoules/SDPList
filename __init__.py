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
@app.route('/')
def index():
	projects = client.projects.find(limit=6)
	return render_template("index.html", projects=list(projects))


if __name__ == '__main__':
    app.run()

