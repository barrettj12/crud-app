#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   __init__.py
#   Initialisation for app package


# Set up app
from flask import Flask
app = Flask(__name__)

# Import other files/methods
from app import admin, apis, helpers
from app.helpers import abort
from flask import request


# Constants
ALLOWED_ORIGINS = {
    'https://barrettj12.github.io',
    'http://127.0.0.1:5500',
    None            # probably should remove this later
}


# Pre/post methods
@app.before_request
def preReq():
    # Check requests are allowed from this origin
    if request.origin not in ALLOWED_ORIGINS:
        abort(403, 'Requests not allowed from your domain: ' + str(request.origin))

@app.after_request
def postReq(response):
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = request.origin
    response.headers['Access-Control-Allow-Headers'] = 'Authorization'
    response.headers['Access-Control-Allow-Methods'] = '*'

    return response


# Run app
if __name__ == '__main__':
    app.run()