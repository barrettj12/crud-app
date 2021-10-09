# Initiate Flask
from flask import Flask, request, abort
from flask.helpers import make_response
app = Flask(__name__)

# Constants
ALLOWED_ORIGINS = {
  "https://barrettj12.github.io",
  "http://127.0.0.1:5500"
}


@app.route('/test')
def testResponse():
  # Check origin is allowed
  if request.origin not in ALLOWED_ORIGINS:
    abort(403, "Requests not allowed from your domain")

  response = make_response('Testing, testing, 1, 2, 3, ...')
  response.headers['Access-Control-Allow-Origin'] = request.origin
  return response