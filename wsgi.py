#   CRUD APP
#     https://github.com/barrettj12/crud-app
#   Author: Jordan Mitchell Barrett (@barrettj12)
#     https://github.com/barrettj12
#
#   /wsgi.py
#   Run app on WSGI server

import app
thisApp = app.create_app()

if __name__ == "__main__":
  thisApp.run()