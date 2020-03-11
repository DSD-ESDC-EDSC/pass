"""
Created on Tue Jan 22 2020

@author: Noznoc

DESCRIPTION:
This module manages initializes the PostgreSQL database
"""

from psycopg2 import pool
import csv
import json
import osgeo.ogr
import geopandas as gp
import numpy as np
from Config import Config
from GeoDataFrame import GeoDataFrame
from CSVDataFrame import CSVDataFrame
from Centroid import Centroid
from DistanceMatrix import DistanceMatrix
from db import init_logger
import pandas as pd
import utils 

logger = init_logger()

class InitSchema():
    "Create the PostgreSQL database tables"

    def __init__(self, config):
        """Read data files

        Arguments:
            config (object): configuration of files for creating database tables
        """

        try:
            self.config = config # configuration file

            self.poi = utils.read_file(self.config.supply_file, self.config.supply_type, self.config.supply_columns, self.config.required_cols['supply'], self.config.supply_encode)
            self.demand_geo = utils.read_file(self.config.demand_geo_file, self.config.demand_geo_type, self.config.demand_geo_columns, self.config.required_cols[self.config.demand_geo_type], self.config.demand_geo_crs)
            try: 
                self.demand_geo_weight = utils.read_file(self.config.demand_geo_weight_file, self.config.demand_geo_weight_type, self.config.demand_geo_weight_columns, self.config.required_cols[self.config.demand_geo_weight_type], self.config.demand_geo_weight_crs )
                self.centroid = 'weighted'
            except:
                self.centroid = 'geographic'

            self.demand_pop = utils.read_file(self.config.demand_pop_file, self.config.demand_pop_type, self.config.demand_pop_columns, self.config.required_cols[self.config.demand_pop_type], self.config.demand_pop_encode)
            
            logger.info('Data successfully read')
        except Exception as e:
            logger.error(f'Data unsuccessful read: {e}')

        from db import DbConnect
        with DbConnect() as db_conn:
            self.db_conn = db_conn
            self.create_schema()

    def execute_query(self, query, msg=None, params=None):
        """Execute query to either create or store data into database table

        Arguments:
            query (str): query to execute
        """

        try:
            if params:
                self.db_conn.cur.execute(query, params)
            else:
                self.db_conn.cur.execute(query)
                self.db_conn.conn.commit()

            if "SELECT" in query:
                records = pd.DataFrame(self.db_conn.cur.fetchall(), columns=[desc[0] for desc in self.db_conn.cur.description])
                return records

            logger.info(f'Successfully {msg} database table')

        except Exception as e:
            logger.error(f'Unsuccessfully {msg} database table: {e}')

    def create_schema(self):
        "Create each PostgreSQL database table"

        # self.init_demand()
        # self.init_poi()
        self.init_distance_matrix()

    def init_distance_matrix(self, profiles=["car"]):
        "Create distance_matrix database table"

        logger.info(f'Calculating distance matrix for {profiles}...')

        # TO DO: update this so that's it's in the same structure as self.calculated_centroid.df, etc.
        if not hasattr(self, 'centroid_df'):
            self.centroid_df = gp.GeoDataFrame.from_postgis("SELECT * FROM demand;", self.db_conn.conn, geom_col = 'centroid')

        if not hasattr(self, 'poi'):
            self.poi = gp.GeoDataFrame.from_postgis("SELECT * FROM poi;", "retrieved POI", self.db_conn.conn, geom_col = 'point')

        import pdb; pdb.set_trace()

        for profile in profiles:
            # TO DO: this will need to change based on different profiles
            try:
                DM = DistanceMatrix(self.poi, self.centroid_df, self.config.ORS_client, self.config.iso_catchment_range,
                    self.config.iso_catchment_type, self.config.iso_profile, self.config.iso_sleep_time, self.config.dm_metric,
                    self.config.dm_unit, self.config.dm_sleep_time, self.config.ORS_timeout)
                logger.info(f'Successfully calculated distance matrix for {profile}')
            except Exception as e:
                logger.error(f'Unsuccessfully calculated the distance matrix for {profile}: {e}')

            # TO DO: update query for different distance_matrix_* based on mode of transportation (will have to update config.json)
            query_create = """
                        DROP TABLE IF EXISTS distance_matrix_%s;
                        CREATE TABLE distance_matrix_%s(
                        id serial PRIMARY KEY,
                        geouid int""" % (profile, profile)

            # loop through all columns to build query statement to create the distance_matrix_* table
            # TO DO: consider different data type?

            # DM.distance_matrix = DM.distance_matrix.where(pd.notnull(DM.distance_matrix), 'NULL')
            columns = ['geouid']

            for col in DM.distance_matrix.columns.values[1:]:
                col_id = "poiuid_" + "".join([i for i in col if i.isdigit()])
                columns.append(col_id)
                if col == DM.distance_matrix.columns.values[-1]:
                    query_create += ", " + col_id  + " numeric)"
                else:
                    query_create += ", " + col_id  + " numeric"

            self.execute_query(query_create, "created distance_matrix_" + profile)

            #columns = ", ".join(DM.distance_matrix.columns.values.tolist()) # list of columns as a string
            columns = ", ".join(columns)
            rows = DM.distance_matrix.to_numpy().tolist() # list of rows

            # for each row in distance matrix
            for i in DM.distance_matrix.index:
                rows[i] = [str(value) for value in rows[i]] # cast each row value as string
                values = ", ".join(rows[i]) # store a row's values into a list as a string

                # insert row into database table
                query_insert = """ INSERT into distance_matrix_%s (%s) VALUES (%s);
                """ % (profile, columns, values)
                self.execute_query(query_insert, "updated distance_matrix")
                # print(query_insert)
            # create index for distance_matrix table
            self.execute_query("CREATE INDEX idx_distance_matrix_%s ON distance_matrix_%s (%s);" % (profile, profile, columns), "indexed distance_matrix_%s" % (profile))

    def init_poi(self):
        "Create the poi database table"

        # create poi table
        query_create = """
            DROP TABLE IF EXISTS poi;
            CREATE TABLE poi(
            id serial PRIMARY KEY,
            geouid text,
            LRG_ID text,
            supply int, 
            point geometry(POINT,3347)
        """ 
        # TO DO: is (POINT, 3347) converting point to 3347 crs or assuming that it's already 3347 crs?

        sql_columns = ['id', 'geouid', 'lrg_id', 'supply', 'point']

        req_columns = ['id', 'geouid', 'lrg_id', 'supply']
        info_columns = [col for col in self.poi if col.startswith('info')]

        self.poi.reset_index(inplace = True)
        self.poi.rename(columns = {'index': 'id'}, inplace = True)

        # self.poi['point'] = utils.create_point(self.poi.longitude, self.poi.latitude)

        if 'supply' not in self.poi.columns: 
            self.poi['supply'] = 1

        for col in [col for col in self.poi if col.startswith('info')]:
            if self.poi[col].dtype == 'O':
                unit = 'text'
            else: 
                unit = 'int'

            sql_columns.append(col)
            query_create = query_create + """,  %s %s""" % (col, unit)

        query_create = query_create + """)"""

        self.execute_query(query_create, "created poi")

        # self.poi = self.poi[sql_columns]

        sql_col_string = '"' + '", "'.join(sql_columns) + '"'

        for i in self.poi.index:
            values = self.poi.loc[i] # .astype(str).values.flatten().tolist()

            vals_default = "'" + "', '".join(values[req_columns].astype(str).values.flatten().tolist()) + "'"
            lat = values['latitude']
            lng = values['longitude']
            vals_info = "'" + "', '".join(values[info_columns].astype(str).values.flatten().tolist()) + "'"

            query_insert = """ INSERT into poi(%s) VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s),3347),%s);
            """ % (sql_col_string, vals_default, lng, lat, vals_info)
           
            self.execute_query(query_insert, "updated poi")

        # create index for poi table
        self.execute_query("CREATE INDEX idx_poi ON poi USING GIST(point);", "indexed poi")

    def init_demand(self):
        "Create the demand database table"

        if self.centroid == 'weighted':
            #

            self.demand_geo_weight = self.demand_geo_weight.merge(self.demand_pop, on = 'geouid')

            centroid = Centroid(self.demand_geo, self.demand_geo_weight)
            self.centroid_df = centroid.calculate_weighted_centroid()

        else:
            self.demand_geo = self.demand_geo.merge(self.demand_pop, on = 'geouid')

            centroid = Centroid(self.demand_geo)
            self.centroid_df = centroid.calculate_geographic_centroid()

        centroid_df = self.centroid_df.copy(deep = True)

        centroid_df['centroid'] = [x.wkt for x in centroid_df['centroid']]

        centroid_df.reset_index(inplace = True)

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
        self.execute_query(query_create, "created demand")

        # loop through all features
        for i in range(layer.GetFeatureCount()):
            # import pdb; pdb.set_trace()
            feature = layer.GetFeature(i) # index value
            fuid = feature.GetField('geouid') # id
            centroid = feature.GetField('centroid') # centroid
            if centroid.startswith("POINT (-n") or centroid.startswith("POINT (n"):
            	centroid = feature.GetGeometryRef().Centroid().ExportToWkt()
            pop = feature.GetField('demand') # population / weight ?
            geometry = feature.GetGeometryRef()
            wkt = geometry.ExportToWkt()
            self.execute_query("INSERT INTO demand (geoUID, boundary, centroid, pop) VALUES (%s,ST_SetSRID(ST_GeomFromText(%s),3347),%s,%s);", "updated demand", (fuid,wkt,centroid,pop))
            self.db_conn.conn.commit()

        # create index for demand table
        self.execute_query("CREATE INDEX idx_demand ON demand USING GIST(centroid, boundary);", "indexed demand")

if __name__ == "__main__":
   config = Config('config.json')

   db_schema = InitSchema(config)
