#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /test/conftest.py
#   Provide common fixtures for tests


import pytest

from app import create_app
from app.helpers import initDB


# Sets up a test client and initialises fresh local database
@pytest.fixture
def client():
    # Import database address from /test/dbconfig.py
    try:
        from dbconfig import DATABASE_URL # type: ignore
        print('Using database URL from /test/dbconfig.py')
    except ImportError as e:
        raise RuntimeError('No database URL has been provided for testing. To provide the database URL, create a file /test/dbconfig.py which defines a variable DATABASE_URL.') from e

    print(f'Database URL is {DATABASE_URL}')


    # Create app for testing
    app = create_app(DATABASE_URL)

    with app.test_client() as client:
        with app.app_context():
            # Set up database
            initDB()
            yield client