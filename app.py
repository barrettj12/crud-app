from flask import Flask

app = Flask(__name__)


@app.route('/test')
def testResponse():
  return 'Testing, testing, 1, 2, 3, ...'