# Imports
import os
import psycopg2
from psycopg2.sql import SQL, Identifier
from flask import Flask, request, abort
#from flask.helpers import make_response
from flask.json import jsonify
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine

# Constants
ALLOWED_ORIGINS = {
    'https://barrettj12.github.io',
    'http://127.0.0.1:5500',
    None            # probably should remove this later
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
        abort(403, description = 'Requests not allowed from your domain: ' + str(request.origin))

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
    # Get provided parameters (in POST body)
    name = request.form.get('name')
    pwd = request.form.get('pwd')
    print('name is "' + name + '" : ' + str(type(name)))
    print('pwd is "' + pwd + '"')

#    if name is None or name == "":
    if not name:
        abort(400, description = 'Please provide a table name.')

    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check table doesn't already exist
    cur.execute('SELECT name FROM tables WHERE name = %s', (name,))
    names = cur.fetchone()

    if names:
        abort(409, description = 'There is already a table called "' +
                                  name + '". Please pick a different name.')

    # Create the table
    cur.execute(
        SQL('CREATE TABLE {} (id INT GENERATED ALWAYS AS IDENTITY);').format(Identifier(name))
    )

    # Enter table in master list 'tables'
    if pwd:
        cur.execute('INSERT INTO tables (name, pwd) VALUES (%s, %s)', (name, pwd))
    else:
        cur.execute('INSERT INTO tables (name) VALUES (%s)', (name,))
        

    # Commit and disconnect from DB
    conn.commit()
    cur.close()
    conn.close()

    return 'Table "' + name + '" successfully created.'



# ADMIN METHODS
# These are ONLY for testing and should be commented out in production

# Reset all data in database
@app.route('/reset')
def reset():
    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Delete all existing data
    #
    cur.execute(
     """DROP SCHEMA public CASCADE;
        CREATE SCHEMA public;
        GRANT ALL ON SCHEMA public TO postgres;
        GRANT ALL ON SCHEMA public TO public;
        COMMENT ON SCHEMA public IS 'standard public schema';"""
    )

    # Create the master list 'tables'
    cur.execute(
     """CREATE TABLE tables (
            id INT GENERATED ALWAYS AS IDENTITY,
            name TEXT NOT NULL,
            pwd TEXT
        );"""
    )

    # Enter table in master list 'tables'
    cur.execute("INSERT INTO tables (name) VALUES ('tables');")

    # Commit and disconnect from DB
    conn.commit()
    cur.close()
    conn.close()

    return 'Reset successful.'


# Get list of tables
@app.route('/tables')
def getTables():
    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute('SELECT * FROM tables')
    tables = cur.fetchall()     # Returns list of tuples

    # Commit and disconnect from DB
    conn.commit()
    cur.close()
    conn.close()

    # Encode 'tables' data as JSON
    return jsonify(
        name = 'tables',
        fields = ["id", "name", "pwd"],
        data = tables
    )