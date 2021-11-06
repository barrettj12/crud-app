#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /app/helpers.py
#   Helper methods for APIs


# Imports
from contextlib import contextmanager
from flask import abort as fabort, current_app, make_response
import psycopg2


# DATABASE METHODS

# Wrapper method for database logic
# Open connection to DB, run code, commit and close
@contextmanager
def dbWrap():
    # Connect to DB
    conn = psycopg2.connect(current_app.config['DATABASE_URL'])
    cur = conn.cursor()

    try:
        yield cur   # Pass cur back to function
        
    finally:
        # Commit and disconnect from DB
        conn.commit()
        cur.close()
        conn.close()


# Reset/initialise database
def initDB():
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


# PARAMETER VALIDATION

# Check table exists and password is correct
def checkTablePwd(name, pwd, cur):
    # Check table exists
    cur.execute('SELECT name FROM tables WHERE name = %s;', (name,))
    names = cur.fetchone()

    if not names:
        abort(404, f'There is no table called "{name}".')

    # Check password
    cur.execute('SELECT pwd FROM tables WHERE name = %s;', (name,))
    storedPwd = cur.fetchone()[0]

    if storedPwd and pwd != storedPwd:
        abort(403, f'Incorrect password for table "{name}".')


# Check table name is not null or forbidden
def checkName(name: str, action: str):
    if not name:
        abort(400, 'Please provide a table name.')
    elif name == 'tables':
        abort(403, f'Not allowed to {action} table "tables".')


# Check row/column name is not null
def checkRowCol(tablename: str, action: str, rcname: str, rctype: str):
    if not rcname:
        ident = 'id' if rctype == 'row' else 'name'
        
        abort(400, f'Please provide the {ident} of the {rctype} you would like to {action} in table "{tablename}".')


# OTHER

# Abort with plain text instead of HTML
def abort(status_code, message):
    response = make_response(message)
    response.status_code = status_code
    fabort(response)


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
