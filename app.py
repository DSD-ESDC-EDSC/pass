from base64 import b64decode
from flask import Flask, request, render_template, jsonify, redirect, url_for, abort, make_response
from waitress import serve
import json
import decimal
import sys
from modules import db, model
from dotenv import load_dotenv
import os
import geopandas as gpd
from geojson import Feature, FeatureCollection, Polygon
from shapely import wkt
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
def run_model():
    req = request.get_json()
    beta = float(req['beta'])
    transportation = req['transportation']
    threshold = int(req['threshold']) * 60 # multiply to get the minute threshold to match distance matrix time unit (ms)
    bounds = req['bounds']

    scores = model.accessibility(bounds, beta, transportation, threshold)
    scores['boundary'] = scores['boundary'].apply(wkt.loads)
    features = scores.apply(
        lambda row: Feature(geometry=row['boundary'], properties={'geouid':row['geouid'], 'score':row['scores']}),
        axis=1).tolist()

    feature_collection = FeatureCollection(features=features)
    feature_collection = json.dumps(feature_collection)

    return feature_collection

# route for bad HTTP requests
@app.errorhandler(400)
def error(e):
    return render_template('error.html')

if __name__ == '__main__':
    serve(app, host=APP_HOST,port=APP_PORT,threads=APP_THREADS)
