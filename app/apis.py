#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /app/apis.py
#   APIs provided by the app


# Imports
from app import app
from app.helpers import abort, checkName, checkRowCol, checkTablePwd, dbWrap, getCols
from flask import request
from flask.json import jsonify
from psycopg2.sql import Identifier, SQL


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
    # print(f'name is "{name}" : {type(name))}')
    # print(f'pwd is "{pwd}"')

    with dbWrap() as cur:
        # Check table doesn't already exist
        cur.execute('SELECT name FROM tables WHERE name = %s;', (name,))
        names = cur.fetchone()

        if names:
            abort(409, f'There is already a table called "{name}". Please pick a different name.')

        # Create the table
        cur.execute(
            SQL('CREATE TABLE {} (id INT GENERATED ALWAYS AS IDENTITY);').format(Identifier(name))
        )

        # Enter table in master list 'tables'
        if pwd:
            cur.execute('INSERT INTO tables (name, pwd) VALUES (%s, %s);', (name, pwd))
        else:
            cur.execute('INSERT INTO tables (name) VALUES (%s);', (name,))

    return f'Table "{name}" successfully created.'


# View existing table (must provide password)
@app.route('/viewtable', methods = ['GET'])
def viewTable():
    name = request.args.get('name')     # sent in query string
    checkName(name, "view")
    pwd = request.headers.get('Authorization')      # sent as auth header

    # Optional sort parameters
    sortby = request.args.get('sortby') or 'id'
    asc = request.args.get('asc') != 'false'

    with dbWrap() as cur:
        # Check table and password
        checkTablePwd(name, pwd, cur)

        # Get table fields
        cols = getCols(name, cur)

        # Get table data
        cur.execute(
            SQL(
            """SELECT *
                FROM {name}
                ORDER BY {col} {dir};"""
            ).format(
              name = Identifier(name),
              col = SQL(sortby),
              dir = SQL('ASC' if asc else 'DESC')
            )
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

    return f'Successfully added row to table "{tablename}".'


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
        print(rows)

        if int(rowid) not in rows:
            abort(404, f'Row "{rowid}" doesn\'t exist in table "{tablename}".')

        # Delete row from table
        cur.execute(
            SQL(
                'DELETE FROM {tn} WHERE id = %s;'
            ).format(
                tn = Identifier(tablename)
            ),
            (rowid,)
        )

    return f'Successfully deleted row "{rowid}" from table "{tablename}".'


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
        # abort(400, f'Please provide a valid datatype for the new column "{colname}" in table "{tablename}". Possible options are: {', '.join(f'"{k}"' for k in DATATYPES)}.')

    with dbWrap() as cur:
        # Check table and password
        checkTablePwd(tablename, pwd, cur)

        # Check column doesn't already exist
        cols = getCols(tablename, cur)

        if colname in cols:
            abort(409, f'Column "{colname}" already exists in table "{tablename}".')

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

    return f'Successfully added column "{colname}" to table "{tablename}".'


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
            abort(404, f'Column "{colname}" doesn\'t exist in table "{tablename}".')

        # Delete column from table
        cur.execute(
            SQL(
                'ALTER TABLE {tn} DROP COLUMN {cn};'
            ).format(
                tn = Identifier(tablename),
                cn = Identifier(colname)
            )
        )

    return f'Successfully deleted column "{colname}" from table "{tablename}".'


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
            abort(404, f'Column "{colname}" already exists in table "{tablename}".')

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

    return f'Successfully updated row "{rowid}", column "{colname}" in table "{tablename}" with the value "{newval}".'


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

    return f'Table "{name}" successfully deleted.'
