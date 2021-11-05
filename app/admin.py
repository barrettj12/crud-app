#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /app/admin.py
#   Admin APIs - should not be accessible in the final app


# Imports
from app import app
from app.helpers import dbWrap
from flask.json import jsonify


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

