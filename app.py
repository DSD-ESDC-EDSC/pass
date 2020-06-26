from base64 import b64decode
from flask import Flask, request, render_template
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

# create flask app
app = Flask(__name__)
app.debug = True
app.secret_key = APP_SECRET_KEY

# logger
logger = db.init_logger()

# route for main page
@app.route('/')
def index():
    poi = json.dumps(db.get_poi())
    demand_cols = db.get_demand_columns()
    supply_cols = db.get_supply_columns()
    capacity_cols = db.get_capacity_columns()

    return render_template('index.html', poi=poi, supply_cols=supply_cols, demand_cols=demand_cols, capacity_cols=capacity_cols)

# route for running enhanced 3SFCA model
@app.route('/model',methods=['POST'])
def run_model():
    req = request.get_json()
    
    try:
        beta = float(req['beta'])
        transportation = req['transportation']
        threshold = int(req['threshold']) * 1000 # multiply to get the minute threshold to match distance matrix meter units
        bounds = req['bounds']
        logger.info(f'User parameters include beta: {beta}, transport: {transportation}, threshold: {threshold}')
    except Exception as e:
        logger.error(f'Parameters provided are incorrect: {e}')
        return e

    supply = req['supply']
    demand = req['demand']
    capacity = req['capacity']

    scores = model.accessibility(bounds, beta, transportation, threshold, demand, supply, capacity)
    scores_col = str(list(scores.columns.values))
    scores_row = str(scores.index)
    max = scores['scores'].max()
    
    try:
        scores['boundary'] = scores['boundary'].apply(wkt.loads)
        features = scores.apply(
            lambda row: Feature(geometry=row['boundary'], properties={'geouid':row['geouid'], 'score':row['scores']}),
            axis=1).tolist()
        feature_collection = FeatureCollection(score_vals=scores['scores'].tolist(), max=max, features=features)
        feature_collection = json.dumps(feature_collection)
        return feature_collection
    except Exception as e:
        logger.error(f'{scores_row}')
        logger.error(f'{scores_col}')
        logger.error(f'Could not return results as geojson: {e}')
        return e

# route for bad HTTP requests
@app.errorhandler(400)
def error(e):
    return render_template('error.html')

if __name__ == '__main__':
    serve(app, host=APP_HOST,port=APP_PORT,threads=APP_THREADS)
