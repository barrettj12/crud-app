#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /test/test_invalid.py
#   Testing invalid requests to the APIs


# Test invalid requests to /maketable
def test_invalid_maketable(client):
    # Invalid method
    assert client.get('/maketable').status_code == 405

    # Name not provided
    assert client.post('/maketable').status_code == 400

    # Reserved name
    assert client.post('/maketable',
        data = {'name': 'tables'}
    ).status_code == 403


# Test invalid requests to /viewtable
def test_invalid_viewtable(client):
    # Invalid method
    assert client.post('/viewtable').status_code == 405

    # Name not provided
    assert client.get('/viewtable').status_code == 400

    # Reserved name
    assert client.get('/viewtable?name=tables').status_code == 403


# Need to create table and test access