import psycopg2 as pg
from psycopg2 import pool
import geoalchemy2 import Geometry
import sqlalchemy import *
import csv
import json
import shapefile as shp
import geopandas as gpd
from weighted_centroid import *
from dotenv import load_dotenv
import os
import re
load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

#pg_pool = pool.SimpleConnectionPool(1,5, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME)

class dbConnect:
	def __init__(self):
		self.db = create_engine('postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+':socket/'+DB_NAME, poolclass=NullPool)

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.db.close()

# function that creates the geography table
def initSchema(data_file=None, geo_file=None):
	with dbConnect() as dbConn:

		initDemand(dbConn)

		dbConn.cur.execute("""
		DROP TABLE IF EXISTS geo_canada;
		CREATE TABLE geo_canada(
		id serial PRIMARY KEY,
		name text,
		code int,
		geom geometry(geometry,4326))
		""")
		dbConn.conn.commit()

		if geo_file:
			data = json.load(geo_file)
		else:
			with open('../data/nilfa.geojson', 'r') as f:
				data = json.load(f)

		query = """
			INSERT INTO geo_canada(name, code, geom)
			VALUES(%s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))"""

		for feature in data['features']:
			#print(feature['properties']['name'])
			geometry = json.dumps(feature['geometry'])
			name = feature['properties']['name']
			code = feature['properties']['code']
			dbConn.cur.execute(query, (name, code, geometry))

		dbConn.conn.commit()

def initDemand():

	# read shapefiles for large (lg) (e.g., Dissemination Areas) and small (sm) (e.g., Dissemination Blocks) geometric boundaries
	shapefile_lg = read_files("../data/demand_lg.shp", 'shape')
	shapefile_sm = read_files("../data/demand_sm.shp", 'shape')
	shapefile_sm_pop = read_files("../data/ddemand_sm_population.csv", 'csv', 'latin-1')

	# dbConn.cur.execute("""
	# DROP TABLE IF EXISTS demand;
	# CREATE TABLE demand(
	# id serial PRIMARY KEY,
	# geoUID int,
	# boundary geometry(geometry,3347)
	# population int
	# """)
	# dbConn.conn.commit()
	#
	# if data_file:
	# 	next(data_file)
	# 	dbConn.cur.copy_from(data_file, 'geo_communities', sep='|', columns=('name','code','region','longitude','latitude','total'))
	# else:
	# 	with open('../data/nunavut_communities.csv', 'r') as data:
	# 		next(data)
	# 		dbConn.cur.copy_from(data, 'geo_communities', sep='|', columns=('name','code','region','longitude','latitude','total'))
	#
	# dbConn.conn.commit()
	#
	# dbConn.cur.execute("""
	# ALTER TABLE geo_communities ADD COLUMN geom geometry(POINT,4326);
	# UPDATE geo_communities SET geom = ST_SetSRID(ST_MakePoint(longitude,latitude),4326);
	# CREATE INDEX idx_geography_geom ON geo_communities USING GIST(geom);
	# """)
	# dbConn.conn.commit()

initDemand()

def queryCommunities():
	with dbConnect() as dbConn:

		dbConn.cur.execute("""
		SELECT json_build_object('name', name, 'code', code, 'geometry', ARRAY[ST_X(geom),ST_Y(geom)], 'total', total)
		FROM geo_communities
		""")

		records = [r[0] for r in dbConn.cur.fetchall()]
		return records

def queryCanada():
	with dbConnect() as dbConn:

		dbConn.cur.execute("""
		SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(features.feature))
		FROM (
			SELECT jsonb_build_object('type', 'Feature', 'geometry', ST_AsGeoJSON(geom)::jsonb, 'properties', to_jsonb(inputs) - 'geom' - 'id'
		) AS feature
			FROM (
				SELECT * FROM geo_canada) inputs) features;
		""")

		records = [r[0] for r in dbConn.cur.fetchall()]
		return records
