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
DATATYPES = {
    'str': 'TEXT',
    'int': 'INT'
}


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
    response.headers['Access-Control-Allow-Headers'] = 'Authorization'
    return response


# Landing page
@app.route('/', methods = ['GET'])
def landingPage():
    return "This is the backend API for crud-app. See https://github.com/barrettj12/crud-app"

# API test interface
@app.route('/test', methods = ['GET'])
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

    if not name:
        abort(400, description = 'Please provide a table name.')

    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check table doesn't already exist
    cur.execute('SELECT name FROM tables WHERE name = %s;', (name,))
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
        cur.execute('INSERT INTO tables (name, pwd) VALUES (%s, %s);', (name, pwd))
    else:
        cur.execute('INSERT INTO tables (name) VALUES (%s);', (name,))
        

    # Commit and disconnect from DB
    conn.commit()
    cur.close()
    conn.close()

    return 'Table "' + name + '" successfully created.'


# View existing table (must provide password)
@app.route('/viewtable', methods = ['GET'])
def viewTable():
    name = request.args.get('name')     # sent in query string
    pwd = request.headers.get('Authorization')      # sent as auth header

    if not name:
        abort(400, description = 'Please provide a table name.')
    elif name == 'tables':
        abort(403, description = 'Not allowed to view table "tables".')

    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check table exists
    cur.execute('SELECT name FROM tables WHERE name = %s;', (name,))
    names = cur.fetchone()

    if not names:
        abort(404, description = 'There is no table called "' + name + '".')

    # Check password
    cur.execute('SELECT pwd FROM tables WHERE name = %s;', (name,))
    storedPwd = cur.fetchone()[0]

    if storedPwd and pwd != storedPwd:
        abort(403, description = 'Incorrect password for table "' + name + '".')

    # Get table fields
    cur.execute(
     """SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
        AND table_schema = 'public';""",
        (name,)
    )
    cols = [x[0] for x in cur.fetchall()]  # flatten inner tuples

    # Get table data
    cur.execute(
        SQL('SELECT * FROM {};').format(Identifier(name))
    )
    tableData = cur.fetchall()     # Returns list of tuples

    # Commit and disconnect from DB
    conn.commit()
    cur.close()
    conn.close()

    # Encode 'tables' data as JSON
    return jsonify(
        name = name,
        fields = cols,
        data = tableData
    )


# Add (empty) row to existing table
@app.route('/addrow', methods=['POST'])
def addRow():
    tablename = request.args.get('name')     # sent in query string
    pwd = request.headers.get('Authorization')      # sent as auth header

    # Check request is proper
    if not tablename:
        abort(400, description = 'Please provide a table name.')
    elif tablename == 'tables':
        abort(403, description = 'Not allowed to modify table "tables".')

    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check table exists
    cur.execute('SELECT name FROM tables WHERE name = %s;', (tablename,))
    names = cur.fetchone()

    if not names:
        abort(404, description = 'There is no table called "' + tablename + '".')

    # Check password
    cur.execute('SELECT pwd FROM tables WHERE name = %s;', (tablename,))
    storedPwd = cur.fetchone()[0]

    if storedPwd and pwd != storedPwd:
        abort(403, description = 'Incorrect password for table "' + tablename + '".')

    # Add new column to table
    cur.execute(
        SQL('INSERT INTO {} DEFAULT VALUES;').format(Identifier(tablename))
    )        

    # Commit and disconnect from DB
    conn.commit()
    cur.close()
    conn.close()

    return 'Successfully added row to table "' + tablename + '".'


# Add column to existing table
@app.route('/addcol', methods=['POST'])
def addCol():
    tablename = request.args.get('name')     # sent in query string
    colname = request.args.get('newcol')
    datatype = request.args.get('datatype')
    pwd = request.headers.get('Authorization')      # sent as auth header

    # Check request is proper
    if not tablename:
        abort(400, description = 'Please provide a table name.')
    elif tablename == 'tables':
        abort(403, description = 'Not allowed to modify table "tables".')
    elif not colname:
        abort(400, description = 'Please provide a name for the new column in table "' + tablename + '".')
    elif not datatype:
        abort(400, description = 'Please provide the datatype for the new column "' + colname + '" in table "' + tablename + '". Possible options are: ' + (', '.join(f'"{k}"' for k in DATATYPES.keys)) + '.')

    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check table exists
    cur.execute('SELECT name FROM tables WHERE name = %s;', (tablename,))
    names = cur.fetchone()

    if not names:
        abort(404, description = 'There is no table called "' + tablename + '".')

    # Check password
    cur.execute('SELECT pwd FROM tables WHERE name = %s;', (tablename,))
    storedPwd = cur.fetchone()[0]

    if storedPwd and pwd != storedPwd:
        abort(403, description = 'Incorrect password for table "' + tablename + '".')

    # Add new column to table
    cur.execute(
        SQL(
            'ALTER TABLE {tn} ADD COLUMN {cn} {dt};'
        ).format(
            tn = Identifier(tablename),
            cn = Identifier(colname),
            dt = SQL(DATATYPES[datatype])
        )
    )        

    # Commit and disconnect from DB
    conn.commit()
    cur.close()
    conn.close()

    return 'Successfully added column "' + colname + '" to table "' + tablename + '".'


# Delete existing table (must provide password)
@app.route('/deletetable', methods = ['DELETE'])
def deleteTable():
    name = request.args.get('name')     # sent in query string
    pwd = request.headers.get('Authorization')      # sent as auth header

    if not name:
        abort(400, description = 'Please provide a table name.')
    elif name == 'tables':
        abort(403, description = 'Not allowed to delete table "tables".')

    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check table exists
    cur.execute('SELECT name FROM tables WHERE name = %s;', (name,))
    names = cur.fetchone()

    if not names:
        abort(404, description = 'There is no table called "' + name + '".')

    # Check password
    cur.execute('SELECT pwd FROM tables WHERE name = %s;', (name,))
    storedPwd = cur.fetchone()[0]

    if storedPwd and pwd != storedPwd:
        abort(403, description = 'Incorrect password for table "' + name + '".')

    # Drop table
    cur.execute(
        SQL('DROP TABLE {};').format(Identifier(name))
    )

    # Delete entry from master list
    cur.execute('DELETE FROM tables WHERE name = %s;', (name,))

    # Commit and disconnect from DB
    conn.commit()
    cur.close()
    conn.close()

    return 'Table "' + name + '" successfully deleted.'




# ADMIN METHODS
# These are ONLY for testing and should be commented out in production

# Reset all data in database
@app.route('/reset', methods = ['DELETE'])
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
@app.route('/tables', methods = ['GET'])
def getTables():
    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute('SELECT * FROM tables;')
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