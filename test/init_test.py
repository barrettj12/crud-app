#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /test/init_test.py
#   Tests for initialisation of app


from app.helpers import dbWrap, getCols

# Test that the database was initialised correctly
def test_db_init(client):
    with dbWrap() as cur:
        # Check that only one table 'tables' has been created
        cur.execute(
         """SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public';"""
        )
        assert cur.fetchall() == [('tables',)]

        # Check columns of 'tables' are right
        assert getCols('tables', cur) == ['id', 'name', 'pwd']

        # Check data in 'tables' is right
        cur.execute('SELECT * FROM tables;')
        data = cur.fetchall()
        assert data == [(1, 'tables', None)]

        