# Imports
import os
import psycopg2
from psycopg2.sql import SQL, Identifier
from flask import Flask, request, abort
#from flask.helpers import make_response
from flask.json import jsonify
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine
from contextlib import contextmanager

# Constants
ALLOWED_ORIGINS = {
    'https://barrettj12.github.io',
    'http://127.0.0.1:5500',
    None            # probably should remove this later
}
DATABASE_URL = os.environ['DATABASE_URL']
#DATATYPES = {
#    'str': 'TEXT',
#    'int': 'INT'
#}


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
    response.headers['Access-Control-Allow-Methods'] = '*'

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
    checkName(name, "create")

    pwd = request.form.get('pwd')
    print('name is "' + name + '" : ' + str(type(name)))
    print('pwd is "' + pwd + '"')

    with dbWrap() as cur:
        # Check table doesn't already exist
        cur.execute('SELECT name FROM tables WHERE name = %s;', (name,))
        names = cur.fetchone()

        if names:
            abort(409, description = 'There is already a table called "' + name + '". Please pick a different name.')

        # Create the table
        cur.execute(
            SQL('CREATE TABLE {} (id INT GENERATED ALWAYS AS IDENTITY);').format(Identifier(name))
        )

        # Enter table in master list 'tables'
        if pwd:
            cur.execute('INSERT INTO tables (name, pwd) VALUES (%s, %s);', (name, pwd))
        else:
            cur.execute('INSERT INTO tables (name) VALUES (%s);', (name,))

    return 'Table "' + name + '" successfully created.'


# View existing table (must provide password)
@app.route('/viewtable', methods = ['GET'])
def viewTable():
    name = request.args.get('name')     # sent in query string
    checkName(name, "view")
    pwd = request.headers.get('Authorization')      # sent as auth header

    with dbWrap() as cur:
        # Check table and password
        checkTablePwd(name, pwd, cur)

        # Get table fields
        cols = getCols(name, cur)

        # Get table data
        cur.execute(
            SQL(
            """SELECT *
                FROM {}
                ORDER BY id ASC;"""
            ).format(Identifier(name))
        )
        tableData = cur.fetchall()     # Returns list of tuples

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
    checkName(tablename, "modify")
    pwd = request.headers.get('Authorization')      # sent as auth header

    with dbWrap() as cur:
        # Check table and password
        checkTablePwd(tablename, pwd, cur)

        # Add new row to table
        cur.execute(
            SQL('INSERT INTO {} DEFAULT VALUES;').format(Identifier(tablename))
        )

    return 'Successfully added row to table "' + tablename + '".'


# Delete given row from table
@app.route('/deleterow', methods=['DELETE'])
def deleteRow():
    tablename = request.args.get('name')     # sent in query string
    rowid = request.args.get('row')
    pwd = request.headers.get('Authorization')      # sent as auth header

    # Check request is proper
    checkName(tablename, 'modify')
    checkRowCol(tablename, 'delete', rowid, 'row')

    with dbWrap() as cur:
        # Check table and password
        checkTablePwd(tablename, pwd, cur)

        # Check row exists
        cur.execute(
            SQL('SELECT id FROM {};').format(Identifier(tablename))
        )
        rows = [x[0] for x in cur.fetchall()]

        if rowid not in rows:
            abort(404, 'Row "' + rowid + '" doesn\'t exist in table "' + tablename + '".')

        # Delete row from table
        cur.execute(
            SQL(
                'DELETE FROM {tn} WHERE id = {rid};'#{dt};'
            ).format(
                tn = Identifier(tablename),
                rid = Identifier(rowid)
            )
        )

    return 'Successfully deleted row "' + rowid + '" from table "' + tablename + '".'


# Add column to existing table
@app.route('/addcol', methods=['POST'])
def addCol():
    tablename = request.args.get('name')     # sent in query string
    colname = request.args.get('col')
    # datatype = request.args.get('datatype')
    pwd = request.headers.get('Authorization')      # sent as auth header

    # Check request is proper
    checkName(tablename, 'modify')
    checkRowCol(tablename, 'add', colname, 'column')
    # elif not datatype or datatype not in DATATYPES:
        # abort(400, description = 'Please provide a valid datatype for the new column "' + colname + '" in table "' + tablename + '". Possible options are: ' + (', '.join(f'"{k}"' for k in DATATYPES)) + '.')

    with dbWrap() as cur:
        # Check table and password
        checkTablePwd(tablename, pwd, cur)

        # Check column doesn't already exist
        cols = getCols(tablename, cur)

        if colname in cols:
            abort(409, 'Column "' + colname + '" already exists in table "' + tablename + '".')

        # Add new column to table
        cur.execute(
            SQL(
                'ALTER TABLE {tn} ADD COLUMN {cn} TEXT;'#{dt};'
            ).format(
                tn = Identifier(tablename),
                cn = Identifier(colname)#,
    #           dt = SQL(DATATYPES[datatype])
            )
        )

    return 'Successfully added column "' + colname + '" to table "' + tablename + '".'


# Delete given column from table
@app.route('/deletecol', methods=['DELETE'])
def deleteCol():
    tablename = request.args.get('name')     # sent in query string
    colname = request.args.get('col')
    pwd = request.headers.get('Authorization')      # sent as auth header

    # Check request is proper
    checkName(tablename, 'modify')
    checkRowCol(tablename, 'delete', colname, 'column')

    with dbWrap() as cur:
        # Check table and password
        checkTablePwd(tablename, pwd, cur)

        # Check column exists
        cols = getCols(tablename, cur)

        if colname not in cols:
            abort(404, 'Column "' + colname + '" doesn\'t exist in table "' + tablename + '".')

        # Delete column from table
        cur.execute(
            SQL(
                'ALTER TABLE {tn} DROP COLUMN {cn};'
            ).format(
                tn = Identifier(tablename),
                cn = Identifier(colname)
            )
        )

    return 'Successfully deleted column "' + colname + '" from table "' + tablename + '".'


# Update cell value in table
@app.route('/update', methods=['PUT'])
def update():
    tablename = request.args.get('name')     # sent in query string
    rowid = request.args.get('row')
    colname = request.args.get('col')
    newval = request.args.get('value')
    pwd = request.headers.get('Authorization')      # sent as auth header

    # Check request is proper
    checkName(tablename, "modify")
    checkRowCol(tablename, 'update', rowid, 'row')
    checkRowCol(tablename, 'update', colname, 'column')

    with dbWrap() as cur:
        # Check table and password
        checkTablePwd(tablename, pwd, cur)

        # Check column exists
        cols = getCols(tablename, cur)

        if colname not in cols:
            abort(404, 'Column "' + colname + '" already exists in table "' + tablename + '".')

        # Add new column to table
        cur.execute(
            SQL(
            """UPDATE {tn}
                SET {cn} = %s
                WHERE id = %s;"""
            ).format(
                tn = Identifier(tablename),
                cn = Identifier(colname)
            ),
            (newval if newval else '', rowid)
        )

    return 'Successfully updated row "' + rowid + '", column "' + colname + '" in table "' + tablename + '" with the value "' + newval + '".'


# Delete existing table (must provide password)
@app.route('/deletetable', methods = ['DELETE'])
def deleteTable():
    name = request.args.get('name')     # sent in query string
    pwd = request.headers.get('Authorization')      # sent as auth header

    checkName(name, "delete")

    with dbWrap() as cur:
        # Check table and password
        checkTablePwd(name, pwd, cur)

        # Drop table
        cur.execute(
            SQL('DROP TABLE {};').format(Identifier(name))
        )

        # Delete entry from master list
        cur.execute('DELETE FROM tables WHERE name = %s;', (name,))

    return 'Table "' + name + '" successfully deleted.'




# ADMIN METHODS
# These are ONLY for testing and should be commented out in production

# Reset all data in database
@app.route('/reset', methods = ['DELETE'])
def reset():
    with dbWrap() as cur:
        # Delete all existing data
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

    return 'Reset successful.'


# Get list of tables
@app.route('/tables', methods = ['GET'])
def getTables():
    with dbWrap() as cur:
        cur.execute('SELECT * FROM tables ORDER BY id ASC;')
        tables = cur.fetchall()     # Returns list of tuples

    # Encode 'tables' data as JSON
    return jsonify(
        name = 'tables',
        fields = ["id", "name", "pwd"],
        data = tables
    )



# HELPER METHODS

# Get column names for a given table
def getCols(name, cur):
    cur.execute(
     """SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
        AND table_schema = 'public';""",
        (name,)
    )

    return [x[0] for x in cur.fetchall()]  # flatten inner tuples


# Check table exists and password is correct
def checkTablePwd(name, pwd, cur):
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


# Wrapper method for database logic
# Open connection to DB, run code, commit and close
@contextmanager
def dbWrap():
    # Connect to DB
    conn = psycopg2.connect(DATABASE_URL)   
    cur = conn.cursor()

    try:
        yield cur   # Pass cur back to function
        
    finally:
        # Commit and disconnect from DB
        conn.commit()
        cur.close()
        conn.close()


# Check table name is not null or forbidden
def checkName(name: str, action: str):
    if not name:
        abort(400, description = 'Please provide a table name.')
    elif name == 'tables':
        abort(403, description = 'Not allowed to ' + action + ' table "tables".')


# Check row/column name is not null
def checkRowCol(tablename: str, action: str, rcname: str, rctype: str):
    if not rcname:
        ident = 'id' if rctype == 'row' else 'name'
        
        abort(400, description = 'Please provide the ' + ident + ' of the ' + rctype + ' you would like to ' + action + ' in table "' + tablename + '".')