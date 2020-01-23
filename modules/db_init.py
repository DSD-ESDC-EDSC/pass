"""
Created on Tue Jan 22 2020

@author: Noznoc

DESCRIPTION:
This module manages initializes the PostgreSQL database
"""

import psycopg2 as pg
from psycopg2 import pool
import csv
import json
import osgeo.ogr
import geopandas as gp
from weighted_centroid import *

class InitSchema(object):
    """Initialize the PostgreSQL database

    Attributes:
        self.db_conn (object):
            database connection
    """

    def __init__(self, poi_path, demand_path_lg, uid, population, demand_path_sm=None, weight=None):
        """Create the PostgreSQL database tables

        Arguments:
            demand_path_lg (str):
                path for demand geodata geodata file
            poi_path (str):
                path for POI csv file
            demand_path_sm (str):
                path for smaller demand geodata file
        """

        from db import DbConnect
        with DbConnect() as db_conn:
            self.db_conn = db_conn
            self.create_schema(weight, population, uid, demand_path_lg, poi_path, demand_path_sm)

    # TO DO function for dynamic reading data files and importing them into db based on values

    def execute_query(self, query):
        """Execute query to either create or store data into database table

        Arguments:
            query (str):
                query to execute
        """

        self.db_conn.cur.execute(query)
        self.db_conn.conn.commit()

    def create_schema(self, weight, population, uid, demand_path_lg, poi_path, demand_path_sm):
        """Create each PostgreSQL database table

        Arguments:
            demand_path_lg (str):
                path for demand geodata geodata file
            poi_path (str):
                path for POI csv file
            demand_path_sm (str):
                path for smaller demand geodata file
        """
        self.init_demand(weight, population, uid, demand_path_lg, demand_path_sm)
        self.init_poi(poi_path)
		# self.initDistanceMatrix()

    def init_poi(self, poi_path):
        """Create the poi PostgreSQL database table

        Arguments:
            poi_path (str):
                path for POI csv file
        """

        # create demand table
        query_create = """
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
        """

        self.execute_query(query_create)

        with open(poi_path, 'r') as data:
        	next(data)
        	self.db_conn.cur.copy_from(data, "poi", sep="|", columns=("geoUID","name","type","address","city","lng","ltd","supply"))
        	self.db_conn.conn.commit()

        query_alter = """
        	ALTER TABLE poi ADD COLUMN point geometry(POINT,4326);
        	UPDATE poi SET point = ST_SetSRID(ST_MakePoint(lng,ltd),4326);
        	CREATE INDEX idx_poi ON poi USING GIST(point);
        """
        self.execute_query(query_alter)

    def init_demand(self, weight, population, uid, demand_path_lg, demand_path_sm=None):
        """Create the demand PostgreSQL database table

        Arguments:
            weight (str):
                population weight column name in the small demand geodata file
            population (str):
                population column name in the large demand geodata file
            uid (str):
                unique id column name in the large demand geodata file
            demand_path_lg (str):
                path for large demand geodata file
            demand_path_sm (str):
                path for smaller demand geodata file
        """

        boundary_lg_gdf = gp.read_file(demand_path_lg)
        boundary_sm_gdf = gp.read_file(demand_path_sm)
        boundary_lg_gdf = calculate_centroid(boundary_sm_gdf, boundary_lg_gdf, uid, weight)
        boundary_lg_gdf = osgeo.ogr.Open(boundary_lg_gdf.to_json())
        layer = boundary_lg_gdf.GetLayer(0)

        # create demand table
        query_create = """
        	DROP TABLE IF EXISTS demand;
        	CREATE TABLE demand(
        	id serial PRIMARY KEY,
        	geoUID int,
        	centroid geometry,
        	boundary geometry,
        	pop int)
        """
        self.execute_query(query_create)

        # loop through all features
        for i in range(layer.GetFeatureCount()):
            feature = layer.GetFeature(i)
            fuid = feature.GetField(uid)
            centroid = feature.GetField("centroid")
            if centroid.startswith("POINT (-n") or centroid.startswith("POINT (n"):
            	centroid = feature.GetGeometryRef().Centroid().ExportToWkt()
            pop = feature.GetField(population)
            geometry = feature.GetGeometryRef()
            wkt = geometry.ExportToWkt()
            self.db_conn.cur.execute("INSERT INTO demand (geoUID, boundary, centroid, pop) VALUES (%s,ST_SetSRID(ST_GeomFromText(%s),3347),%s,%s);", (fuid,wkt,centroid,pop))
            self.db_conn.conn.commit()

        # create index for demand table
        self.execute_query("CREATE INDEX idx_demand ON demand USING GIST(centroid, boundary);")

def main():
    """Runs script as __main__. """

    demand_path_lg = "../data/demand_lg_pop_mtl.shp"
    demand_path_sm = "../data/demand_sm_pop_mtl.shp"
    poi_path = "../data/poi.csv"
    weight = "demand_sm_"
    population = "demand_lg_"
    uid = "DAUID"

    InitSchema(poi_path, demand_path_lg, uid, population, demand_path_sm, weight)

if __name__ == "__main__":
    main()
