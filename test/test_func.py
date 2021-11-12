#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /test/test_func.py
#   Functional tests


# Make and populate a table
#
#           test
#   | id | col1  | col2 |
#   |----|-------|------|
#   | 1  |       | one  |
#   | 2  |       | two  |
#   | 3  | three |      |
#
def test_maketable(client):
    client.post('/maketable',
        data = {'name': 'test'}
    )