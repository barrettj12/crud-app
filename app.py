# Imports
import os
import psycopg2
from flask import Flask, request, abort
from flask.helpers import make_response
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine

# Constants
ALLOWED_ORIGINS = {
    'https://barrettj12.github.io',
    'http://127.0.0.1:5500'
}
DATABASE_URL = os.environ['DATABASE_URL']


# Initiate/configure app
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
#db = SQLAlchemy(app)


# Pre/post methods
@app.before_request
def preReq():
    # Check requests are allowed from this origin
    if request.origin not in ALLOWED_ORIGINS:
        abort(403, description = 'Requests not allowed from your domain')

@app.after_request
def postReq(response):
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = request.origin
    return response


# API test interface
@app.route('/test')
def testResponse():
    return 'This is a test'


# Make new table
@app.route('/maketable', methods=['POST'])
def makeTable():
    # Get provided parameters
    name = request.args.get('name')
    pwd = request.args.get('pwd')

    if name is None:
        abort(400, description = 'Please provide a table name.')

    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check table doesn't already exist
    cur.execute('SELECT name FROM tables WHERE name = %s', name)
    names = cur.fetchone()

    if names is not None:
        abort(409, description = 'There is already a table called "' +
                                  name + '". Please pick a different name.')

    # Create the table
    if pwd is None:
        cur.execute('INSERT INTO tables (name) VALUES (%s)', name)
    else:
        cur.execute('INSERT INTO tables (name, pwd) VALUES (%s, %s)', name, pwd)

    # Commit and disconnect from DB
    conn.commit()
    cur.close()
    conn.close()

    return 'Table "' + name + '"successfully created.'


# Get list of tables
# NB: this method is ONLY for testing and should be commented out in production
@app.route('/tables')
def getTables():
    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute('SELECT * FROM tables')
    tables = cur.fetchone()

    # Commit and disconnect from DB
    conn.commit()
    cur.close()
    conn.close()

    # Returning an int? What the hell is this?
    print('\nTABLES IS', tables, '\n')
    return tables