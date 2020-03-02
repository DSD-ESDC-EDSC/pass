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
import numpy as np
from weighted_centroid import *

from Config import Config
from GeoDataFrame import GeoDataFrame
from CSVDataFrame import CSVDataFrame
from weighted_centroid import WeightedCentroid
from DistanceMatrix import DistanceMatrix

class InitSchema(object):
    """Initialize the PostgreSQL database

    Attributes:
        self.db_conn (object):
            database connection
    """

    def __init__(self, config):
        """Create the PostgreSQL database tables

        Arguments:
            demand_path_lg (str):
                path for demand geodata geodata file
            poi_path (str):
                path for POI csv file
            demand_path_sm (str):
                path for smaller demand geodata file
        """
        self.config = config

        self.poi = CSVDataFrame(self.config.supply_file, self.config.supply_type, self.config.supply_columns, self.config.required_cols['supply'], self.config.supply_encode)
        self.boundary_lg = GeoDataFrame(self.config.lrg_shapefile, self.config.lrgshape_type, self.config.lrgshape_columns, self.config.required_cols[self.config.lrgshape_type], self.config.lrgshape_projection)
        self.boundary_sm = GeoDataFrame(self.config.sml_shapefile, self.config.smlshape_type, self.config.smlshape_columns, self.config.required_cols[self.config.smlshape_type], self.config.smlshape_projection)
        self.small_pop = CSVDataFrame(self.config.sml_popfile, self.config.smlpop_type, self.config.smlpop_columns, self.config.required_cols[self.config.smlpop_type], self.config.smlpop_encode)


        from db import DbConnect
        with DbConnect() as db_conn:
            self.db_conn = db_conn
            self.create_schema()
        
    # TO DO function for dynamic reading data files and importing them into db based on values

    def execute_query(self, query):
        """Execute query to either create or store data into database table

        Arguments:
            query (str):
                query to execute
        """

        self.db_conn.cur.execute(query)
        self.db_conn.conn.commit()

    def create_schema(self):
        """Create each PostgreSQL database table

        Arguments:
            demand_path_lg (str):
                path for demand geodata geodata file
            poi_path (str):
                path for POI csv file
            demand_path_sm (str):
                path for smaller demand geodata file
        """
        self.init_demand()
        self.init_poi()
        self.init_distance_matrix()

    def init_distance_matrix(self):
        # import pdb; pdb.set_trace()

        dm = DistanceMatrix(self.calculated_centroid, self.poi, self.calculated_centroid, self.config.ORS_client, self.config.iso_catchment_range, 
            self.config.iso_catchment_type, self.config.iso_profile, self.config.iso_sleep_time, self.config.dm_metric, 
            self.config.dm_unit, self.config.dm_sleep_time, self.config.ORS_timeout)


    def init_poi(self):
        """Create the poi PostgreSQL database table

        Arguments:
            poi_path (str):
                path for POI csv file
        """

        # create poi table
        query_create = """
            DROP TABLE IF EXISTS poi;
            CREATE TABLE poi(
            id serial PRIMARY KEY,
            geouid text, 
            LRG_ID text,
            latitude float, 
            longitude float, 
            supply int
        """
        sql_columns = ['id', 'geouid', 'lrg_id', 'latitude', 'longitude', 'supply']

        # create POI DataFrame object 

        self.poi.df.reset_index(inplace = True)

        self.poi.df.CMAUID = np.where(self.poi.df.CMAUID == ' ', None, self.poi.df.CMAUID)

        for col in self.poi.get_column_by_type('supply_info'):
            col_name = 'info_' + col.get_colname().lower().replace(" ", "_")
            unit = col.get_sql_colunit()

            sql_columns.append(col_name)
            query_create = query_create + """ ,  %s %s """ % (col_name, unit) 

        query_create = query_create + """)"""

        self.execute_query(query_create)

        sql_col_string = '"' + '", "'.join(sql_columns) + '"'

        for i in self.poi.df.index:

            value_string = "'" + "', '".join(self.poi.df.loc[i].astype(str).values.flatten().tolist()) + "'"

            insert_query = """ INSERT into poi(%s) values (%s); 
            """ % (sql_col_string, value_string)

            self.execute_query(insert_query)

    def init_demand(self):
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

        self.boundary_sm.merge_DataFrame(self.small_pop)

        centroid = WeightedCentroid(self.boundary_lg, self.boundary_sm)
        centroid.calculate_centroid()
        self.calculated_centroid = centroid.boundary_lg
        centroid_df = self.calculated_centroid.df
        centroid_df[self.calculated_centroid.get_column_by_type('centroid').get_colname()] = [x.wkt for x in centroid_df[self.calculated_centroid.get_column_by_type('centroid').get_colname()]]

        centroid_df = osgeo.ogr.Open(centroid_df.to_json())

        layer = centroid_df.GetLayer(0)

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
            # import pdb; pdb.set_trace()
            feature = layer.GetFeature(i) # index value 
            fuid = feature.GetField(self.calculated_centroid.get_column_by_type('ID').get_colname()) # id 
            centroid = feature.GetField(self.calculated_centroid.get_column_by_type('centroid').get_colname()) # centroid 
            if centroid.startswith("POINT (-n") or centroid.startswith("POINT (n"):
            	centroid = feature.GetGeometryRef().Centroid().ExportToWkt()
            pop = feature.GetField(self.calculated_centroid.get_column_by_type('demand').get_colname()) # population / weight ? 
            geometry = feature.GetGeometryRef()
            wkt = geometry.ExportToWkt()
            self.db_conn.cur.execute("INSERT INTO demand (geoUID, boundary, centroid, pop) VALUES (%s,ST_SetSRID(ST_GeomFromText(%s),3347),%s,%s);", (fuid,wkt,centroid,pop))
            self.db_conn.conn.commit()

        # create index for demand table
        self.execute_query("CREATE INDEX idx_demand ON demand USING GIST(centroid, boundary);")

if __name__ == "__main__":
   config = Config('config.json')

   db_schema = InitSchema(config)
