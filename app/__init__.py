#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /app/__init__.py
#   Main file for app package


from flask import Flask

# Constants
ALLOWED_ORIGINS = {
    'https://barrettj12.github.io',
    'http://127.0.0.1:5500',
    None            # probably should remove this later
}


# Application factory
def create_app(dbUrl = None):
    app = Flask(__name__)

    # Configure database url
    if (dbUrl):
        app.config['DATABASE_URL'] = dbUrl
    else:
        # Try to import from db.py file
        try:
            from app.db import DATABASE_URL
            app.config['DATABASE_URL'] = DATABASE_URL
        except ImportError as e:
            raise RuntimeError('No database URL has been provided to the application. You can provide the database URL as an argument to create_app(), or by defining a variable DATABASE_URL in a file /app/db.py.') from e

    # Import helpers
    from app.helpers import abort
    from flask import request

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
        response.headers['Access-Control-Max-Age'] = 86400

        return response

    # Import other APIs
    from app.admin import admin
    app.register_blueprint(admin)
    from app.apis import apis
    app.register_blueprint(apis)
    

    return app
