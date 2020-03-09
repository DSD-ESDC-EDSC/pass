from base64 import b64decode
from flask import Flask, request, render_template, jsonify, redirect, url_for, abort, make_response
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
import json
import sys
from modules import db, model
from dotenv import load_dotenv
import os
import gzip
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3
load_dotenv()

APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY')
APP_HOST = os.environ.get('APP_HOST')
APP_PORT = os.environ.get('APP_PORT')
APP_THREADS = int(os.environ.get('APP_THREADS', 4))

USER_NAME = os.environ.get('USER_NAME')
USER_PASSWORD = os.environ.get('USER_PASSWORD')
ADMIN_NAME = os.environ.get('ADMIN_NAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

HTTP_OK = 200
HTTP_BAD_REQ = 400
HTTP_FORBIDDEN = 403

# create flask app
app = Flask(__name__)
app.debug = True
app.secret_key = APP_SECRET_KEY

# route for NILFA hub / landing page
@app.route('/')
def index():
    poi = json.dumps(db.get_poi())
    #region = json.dumps(db.get_region())
    #demand_point = json.dumps(db.get_demand('point'))
    #demand_boundary = json.dumps(db.get_demand('boundary'))
    return render_template('index.html', poi=poi)

# route for retreiving data for the calculator tool
@app.route('/model',methods=['POST'])
def model():
    req = request.get_json()
    beta = float(req['beta'])
    transportation = req['transportation']
    threshold = int(req['threshold'])
    bounds = req['bounds'] # {'_southWest': {'lat': 45.25362179991922, 'lng': -74.80590820312501}, '_northEast': {'lat': 45.91103315853964, 'lng': -72.49603271484376}}
    test = model.accessibiltiy(bounds, beta, transportation, threshold)
    demand_boundary = json.dumps(db.get_demand('boundary'))
    return demand_boundary

# route for bad HTTP requests
@app.errorhandler(400)
def error(e):
	return render_template('error.html')

if __name__ == '__main__':
	serve(app, host=APP_HOST,port=APP_PORT,threads=APP_THREADS)
