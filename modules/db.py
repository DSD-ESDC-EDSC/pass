import psycopg2 as pg
from psycopg2 import pool
import csv
import json
import osgeo.ogr
import geopandas as gp
from dotenv import load_dotenv
import os
import re
import time
import logging
load_dotenv()


def logger():
	log_levels = {
		'debug': logging.DEBUG,
		'info': logging.INFO,
		'warning': logging.WARNING,
		'error': logging.ERROR,
		'critical': logging.CRITICAL,
	}

	DEFAULT_LOG_LEVEL = os.environ.get('DEFAULT_LOG_LEVEL')

	# initialize logging
	logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
	logger = logging.getLogger(__name__)
	logger.setLevel(log_levels.get(DEFAULT_LOG_LEVEL, logging.INFO))

	return logger

logger = logger()

class DbConnect:
	def __init__(self):
		try:
			self.pg_pool = pool.SimpleConnectionPool(1,5, user=os.environ.get('DB_USER'), password=os.environ.get('DB_PASSWORD'), host=os.environ.get('DB_HOST'), database=os.environ.get('DB_NAME'))
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
def getPOI():
	with DbConnect() as dbConn:

		dbConn.cur.execute("""
		SELECT json_build_object('name', name, 'type', type, 'geometry', ARRAY[ST_X(ST_Transform(point, 4326)),ST_Y(ST_Transform(point, 4326))], 'supply', supply)
		FROM poi
		""")

		records = [r[0] for r in dbConn.cur.fetchall()]
		return records

def getDemand(type):
	with DbConnect() as dbConn:

		if type == 'boundary':
			dbConn.cur.execute("""
			SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(features.feature))
			FROM (
				SELECT jsonb_build_object('type', 'Feature', 'geometry', ST_AsGeoJSON(ST_Transform(ST_Simplify(boundary,0.5), 4326))::jsonb, 'properties', to_jsonb(inputs) - 'boundary' - 'id'
			) AS feature
				FROM (
					SELECT * FROM demand) inputs) features;
			""")

		records = [r[0] for r in dbConn.cur.fetchall()]
		return records
