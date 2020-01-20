import psycopg2 as pg
from psycopg2 import pool
import csv
import json
import osgeo.ogr
import geopandas as gp
# from weighted_centroid import *
from dotenv import load_dotenv
import os
import re
load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

pg_pool = pool.SimpleConnectionPool(1,5, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME)

class dbConnect:
	def __init__(self):
		self.conn = pg_pool.getconn()
		self.cur = self.conn.cursor()

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.cur.close()
		pg_pool.putconn(self.conn)

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

def initPOI(dbConn, data_file=None):
	# create demand table
	dbConn.cur.execute("""
		DROP TABLE IF EXISTS poi;
		CREATE TABLE poi(
		id serial PRIMARY KEY,
		geoUID text,
		name text,
		type text,
		address text,
		city text,
		lng float,
		ltd float,
		supply int)
	""")

	if data_file:
			next(data_file)
			dbConn.cur.copy_from(data_file, 'poi', sep='|', columns=('name','code','region','longitude','latitude','total'))
	else:
		with open('../data/poi.csv', 'r') as data:
			#reader = csv.reader(data)
			#list = [row for row in reader]
			next(data)
			dbConn.cur.copy_from(data, 'poi', sep='|', columns=('geoUID','name','type','address','city','lng','ltd','supply'))

		dbConn.conn.commit()

		dbConn.cur.execute("""
		ALTER TABLE poi ADD COLUMN point geometry(POINT,4326);
		UPDATE poi SET point = ST_SetSRID(ST_MakePoint(lng,ltd),4326);
		CREATE INDEX idx_geography_geom ON poi USING GIST(point);
		""")
		dbConn.conn.commit()

def initDemand(dbConn, weight, population):

	# read shapefiles for large (lg) (e.g., Dissemination Areas) and small (sm) (e.g., Dissemination Blocks) geometric boundaries
	boundary_lg_gdf = read_files("../data/demand_lg_pop_mtl.shp", 'shape')
	boundary_sm_gdf = read_files("../data/demand_sm_pop_mtl.shp", 'shape')
	print(boundary_lg_gdf.head())
	# make sure the return is an updated boundary_lg_gdf
	boundary_lg_gdf = calculate_centroid(boundary_sm_gdf, boundary_lg_gdf, "DAUID", weight)

	boundary_lg_ogr = osgeo.ogr.Open(boundary_lg_gdf.to_json())

	print(list(boundary_lg_gdf))
	print(boundary_lg_gdf.head())

	# create demand table
	dbConn.cur.execute("""
		DROP TABLE IF EXISTS demand;
		CREATE TABLE demand(
		id serial PRIMARY KEY,
		geoUID int,
		centroid geometry,
		boundary geometry,
		pop int)
	""")
	dbConn.conn.commit()

	def addBoundary(layer, uid):

		# loop through all features
		for i in range(layer.GetFeatureCount()):
			feature = layer.GetFeature(i)
			fuid = feature.GetField(uid)
			centroid = feature.GetField('centroid')
			if centroid.startswith('POINT (-n') or centroid.startswith('POINT (n'):
				centroid = feature.GetGeometryRef().Centroid().ExportToWkt()
			pop = feature.GetField(population)
			geometry = feature.GetGeometryRef()
			wkt = geometry.ExportToWkt()
			dbConn.cur.execute("INSERT INTO demand (geoUID, boundary, centroid, pop) VALUES (%s,ST_SetSRID(ST_GeomFromText(%s),3347),%s,%s);", (fuid,wkt,centroid,pop))

		dbConn.conn.commit()

	addBoundary(boundary_lg_ogr.GetLayer(0), "DAUID")

	# create index for demand table
	# dbConn.cur.execute("CREATE INDEX demand_index ON demand USING GIST(centroids, boundary);")
	# dbConn.conn.commit()

	# Push data into db

def getPOI():
	with dbConnect() as dbConn:

		dbConn.cur.execute("""
		SELECT json_build_object('name', name, 'type', type, 'geometry', ARRAY[ST_X(ST_Transform(point, 4326)),ST_Y(ST_Transform(point, 4326))], 'supply', supply)
		FROM poi
		""")

		records = [r[0] for r in dbConn.cur.fetchall()]
		return records

def getDemand(type):
	with dbConnect() as dbConn:

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
