#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /test/maketable_test.py
#   Tests for the /maketable API


# Test invalid requests to /maketable
def test_maketable_invalid(client):
    # Invalid method
    assert client.get('/maketable').status_code == 405

    # Name not provided
    assert client.post('/maketable').status_code == 400

    # Reserved name
    assert client.post('/maketable',
        data = {'name': 'tables'}
    ).status_code == 403


# Make and populate a table