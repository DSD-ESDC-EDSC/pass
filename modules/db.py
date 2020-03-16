from __future__ import unicode_literals
import psycopg2 as pg
from psycopg2 import pool
import csv
import json
import osgeo.ogr
import shutil
import geopandas as gp
from dotenv import load_dotenv
import os
import re
import time
import logging
load_dotenv()

def init_logger():
	log_levels = {
		'debug': logging.DEBUG,
		'info': logging.INFO,
		'warning': logging.WARNING,
		'error': logging.ERROR,
		'critical': logging.CRITICAL,
	}

	LOG_DEFAULT_LEVEL = os.environ.get('LOG_DEFAULT_LEVEL')

	# initialize logging
	logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s',filename=os.environ.get('LOG_FILE_PATH'), filemode='a',level=logging.DEBUG) # to save as log file: filename=os.environ.get('LOG_FILE_PATH'), filemode='a',level=logging.DEBUG)
	logger = logging.getLogger(__name__)
	logger.setLevel(log_levels.get(LOG_DEFAULT_LEVEL, logging.INFO))

	return logger

logger = init_logger()

class DbConnect:
	def __init__(self):
		try:
			self.pg_pool = pool.SimpleConnectionPool(1, 5, user=os.environ.get('DB_USER'), password=os.environ.get('DB_PASSWORD'), host=os.environ.get('DB_HOST'), database=os.environ.get('DB_NAME'))
			self.conn = self.pg_pool.getconn()
			self.cur = self.conn.cursor()
			logger.info('Connection to database succeeded')
		except Exception as e:
			logger.error(f'Connection to database failed: {e}')
		self.start_time = time.time()

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.cur.close()
		self.pg_pool.putconn(self.conn)
		logger.info(f'Released database connection: held for {time.time() - self.start_time} seconds')

## IMPROVE THIS
def get_poi():
	with DbConnect() as db_conn:

		db_conn.cur.execute("""
		SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(features.feature))
		FROM (
			SELECT jsonb_build_object('type', 'Feature', 'geometry', ST_AsGeoJSON(ST_Transform(point, 4326))::jsonb, 'properties', to_jsonb(inputs) - 'point' - 'lng' - 'ltd'
		) AS feature
			FROM (
				SELECT * FROM poi) inputs) features;
		""")

		records = [r[0] for r in db_conn.cur.fetchall()]
		return records

def get_demand(type):
	with DbConnect() as db_conn:

		if type == 'boundary':
			db_conn.cur.execute("""
			SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(features.feature))
			FROM (
				SELECT jsonb_build_object('type', 'Feature', 'geometry', ST_AsGeoJSON(ST_Transform(ST_Simplify(boundary,0.5), 4326))::jsonb, 'properties', to_jsonb(inputs) - 'boundary' - 'id'
			) AS feature
				FROM (
					SELECT * FROM demand) inputs) features;
			""")

		if (type == "point"):
			db_conn.cur.execute("""
			SELECT json_build_object('geometry', ARRAY[ST_X(ST_Transform(centroid, 4326)),ST_Y(ST_Transform(centroid, 4326))])
			FROM demand
			""")

		records = [r[0] for r in db_conn.cur.fetchall()]
		return records
