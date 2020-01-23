import psycopg2 as pg
from psycopg2 import pool
import csv
import json
import osgeo.ogr
import geopandas as gp
from dotenv import load_dotenv
import os
import re
load_dotenv()

class DbConnect:
	def __init__(self):
		self.host = os.environ.get('DB_HOST')
		self.name = os.environ.get('DB_NAME')
		self.user = os.environ.get('DB_USER')
		self.password = os.environ.get('DB_PASSWORD')

	def __enter__(self):
		self.pg_pool = pool.SimpleConnectionPool(1,5, user=self.user, password=self.password, host=self.host, database=self.name)
		self.conn = self.pg_pool.getconn()
		self.cur = self.conn.cursor()
		return self

	def __exit__(self, type, value, traceback):
		self.cur.close()
		self.pg_pool.putconn(self.conn)

# function that creates the geography table

## IMPROVE THIS
def get_poi():
	with DbConnect() as db_conn:

		db_conn.cur.execute("""
		SELECT json_build_object('name', name, 'type', type, 'geometry', ARRAY[ST_X(ST_Transform(point, 4326)),ST_Y(ST_Transform(point, 4326))], 'supply', supply)
		FROM poi
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
