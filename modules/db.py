from __future__ import unicode_literals
import psycopg2 as pg
from psycopg2 import pool
import csv
import json
import osgeo.ogr
import shutil
import geopandas as gp
import time

# when running app
try:
	from modules import config, logger

# when running InitSchema
except:
	import config
	import logger

DB = config.Database()
logger = logger.init()

class DbConnect:
	def __init__(self):
		try:
			self.pg_pool = pool.SimpleConnectionPool(1, 5, user=DB.USER, password=DB.PASSWORD, host=DB.HOST, database=DB.NAME)
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

def get_demand_columns():
	with DbConnect() as db_conn: 
		db_conn.cur.execute(""" 
			SELECT COLUMN_NAME FROM information_schema.columns
			WHERE TABLE_NAME = 'demand'
			AND COLUMN_NAME LIKE 'pop%';
			""")

		columns = db_conn.cur.fetchall()

		col_dict = {}

		for col in columns: 
			col_dict[col[0]] = col[0][4:]

		return col_dict

def get_supply_columns():
	with DbConnect() as db_conn: 
		db_conn.cur.execute(""" 
			SELECT COLUMN_NAME FROM information_schema.columns
			WHERE TABLE_NAME = 'poi'
			AND COLUMN_NAME LIKE 'supply%';
			""")

		columns = db_conn.cur.fetchall()
		
		col_dict = {}

		for col in columns:
			col_dict[col[0]] = col[0][7:]

		return col_dict
		
def get_capacity_columns():
	with DbConnect() as db_conn: 
		db_conn.cur.execute(""" 
			SELECT COLUMN_NAME FROM information_schema.columns
			WHERE TABLE_NAME = 'poi'
			AND COLUMN_NAME LIKE 'capacity%';
			""")

		columns = db_conn.cur.fetchall()
		
		col_dict = {}

		for col in columns:
			col_dict[col[0]] = col[0][9:]

		return col_dict
