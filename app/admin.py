#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /app/admin.py
#   Admin APIs - should not be accessible in the final app


# Imports
# from app import app
from app.helpers import dbWrap, initDB
from flask import Blueprint # current_app
from flask.json import jsonify

# Create blueprint to attach API methods to
admin = Blueprint('admin', __name__)


# Reset all data in database
@admin.route('/reset', methods = ['DELETE'])
def reset():
    initDB()
    return 'Reset successful.'


# Get list of tables
@admin.route('/tables', methods = ['GET'])
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
