#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /wsgi.py
#   Run app on WSGI server

import app

# Find database URL
try:
    from app.dbconfig import DATABASE_URL
    print('Using database URL from /app/dbconfig.py')
except ImportError:
    import os
    try:
        DATABASE_URL = os.environ['DATABASE_URL']
    except KeyError as e:
        raise RuntimeError('No database URL has been provided to the application. You can provide the database URL by (in order of precedence):\n * creating a file /app/dbconfig.py which defines a variable DATABASE_URL;\n * defining an environment variable called "DATABASE_URL".') from e
    
    print('Using database URL from the "DATABASE_URL" environment variable')

print(f'Database URL is {DATABASE_URL}')

# Create app
app = app.create_app(DATABASE_URL)

if __name__ == "__main__":
    app.run()