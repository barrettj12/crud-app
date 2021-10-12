# Imports
import os
import psycopg2
from flask import Flask, request, abort
from flask.helpers import make_response
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine

# Constants
ALLOWED_ORIGINS = {
  "https://barrettj12.github.io",
  "http://127.0.0.1:5500"
}
DATABASE_URL = os.environ['DATABASE_URL']


# Initiate/configure app
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
#db = SQLAlchemy(app)


# API test interface
@app.route('/test')
def testResponse():
  # Check origin is allowed
  if request.origin not in ALLOWED_ORIGINS:
    abort(403, "Requests not allowed from your domain")

  response = make_response({
    "message": "This is a test"
  })
  response.headers['Access-Control-Allow-Origin'] = request.origin
  return response