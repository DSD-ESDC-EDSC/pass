"""
Created on Tue Jan 22 2020

@author: Noznoc

DESCRIPTION:
This module manages initializes the PostgreSQL database
"""

from psycopg2 import pool
import csv
import sys
import json
import osgeo.ogr
import geopandas as gp
import numpy as np
from Config import Config
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
                self.centroid = 'weighted'
                self.demand_geo_weight = utils.read_file(self.config.demand_geo_weight_file, self.config.demand_geo_weight_type, self.config.demand_geo_weight_columns, self.config.required_cols[self.config.demand_geo_weight_type], self.config.demand_geo_weight_crs )
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
        #self.init_demand()
        self.init_poi()
        #self.init_distance_matrix()

    def init_distance_matrix(self, profiles=["car"]):
        "Create distance_matrix database table"

        logger.info(f'Calculating distance matrix for {profiles}...')

        # TO DO: update this so that's it's in the same structure as self.calculated_centroid.df, etc.
        if not hasattr(self, 'centroid_df'):
            self.centroid_df = gp.GeoDataFrame.from_postgis("SELECT * FROM demand;", self.db_conn.conn, geom_col = 'centroid')

        if not hasattr(self, 'poi'):
            self.poi = gp.GeoDataFrame.from_postgis("SELECT * FROM poi;", "retrieved POI", self.db_conn.conn, geom_col = 'point')

        for profile in profiles:
            # TO DO: this will need to change based on different profiles
            try:
                DM = DistanceMatrix(self.poi, self.centroid_df, self.config.ORS_client, self.config.iso_catchment_range,
                    self.config.iso_catchment_type, self.config.iso_profile, self.config.iso_sleep_time, self.config.dm_metric,
                    self.config.dm_unit, self.config.dm_sleep_time, self.config.ORS_timeout)
                logger.info(f'Successfully calculated distance matrix for {profile}')
            except Exception as e:
                logger.error(f'Unsuccessfully calculated the distance matrix for {profile}: {e}')
                sys.exit(1)

            # TO DO: update query for different distance_matrix_* based on mode of transportation (will have to update config.json)
            query_create = """
                        DROP TABLE IF EXISTS distance_matrix_%s;
                        CREATE TABLE distance_matrix_%s(
                        id serial PRIMARY KEY,
                        geouid int""" % (profile, profile)

            # loop through all columns to build query statement to create the distance_matrix_* table
            # TO DO: consider different data type?

            DM.distance_matrix = DM.distance_matrix.where(pd.notnull(DM.distance_matrix), 'NULL')
            columns = ['geouid']

            for col in DM.distance_matrix.columns.values[1:]:
                columns.append(col)
                if col == DM.distance_matrix.columns.values[-1]:
                    query_create += ", " + col  + " float)"
                else:
                    query_create += ", " + col  + " float"

            self.execute_query(query_create, "created distance_matrix_" + profile)

            columns = ", ".join(DM.distance_matrix.columns.values.tolist()) # list of columns as a string
            rows = DM.distance_matrix.to_numpy().tolist() # list of rows

            # for each row in distance matrix
            for i in DM.distance_matrix.index:
                rows[i] = [str(value) for value in rows[i]] # cast each row value as string
                values = ", ".join(rows[i]) # store a row's values into a list as a string

                # insert row into database table
                query_insert = """ INSERT into distance_matrix_%s (%s) VALUES (%s);""" % (profile, columns, values)
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
            "supply_Uniform" float,
            point geometry(POINT,3347)
        """

        # TO DO: is (POINT, 3347) converting point to 3347 crs or assuming that it's already 3347 crs?

        sql_columns = ['id', 'geouid', 'lrg_id', 'supply_Uniform', 'point']

        req_columns = ['id', 'geouid', 'lrg_id', 'supply_Uniform']
        info_columns = [col for col in self.poi if col.startswith('info') or col.startswith('capacity') or col.startswith('supply')]

        self.poi.reset_index(inplace = True)
        self.poi.rename(columns = {'index': 'id'}, inplace = True)

        for col in [col for col in self.poi if col.startswith('info') or col.startswith('capacity') or col.startswith('supply')]:
            if self.poi[col].dtype == 'O':
                unit = 'text'
            else:
                unit = 'numeric'
            sql_columns.append(col)
            query_create = query_create + """,  %s %s""" % ('"' + col + '"', unit)
        
        query_create = query_create + """)"""
        
        if 'supply_Uniform' not in self.poi.columns:
            self.poi['supply_Uniform'] = 1

        self.poi.supply = self.poi['supply_Uniform'].astype(float)
        print(query_create)
        self.execute_query(query_create, "created poi")

        # self.poi = self.poi[sql_columns]

        sql_col_string = '"' + '", "'.join(sql_columns) + '"'

        for i in self.poi.index:
            values = self.poi.loc[i] # .astype(str).values.flatten().tolist()

            vals_default = "'" + "', '".join(values[req_columns].astype(str).values.flatten().tolist()) + "'"
            lat = values['latitude']
            lng = values['longitude']
            if len(info_columns) > 0:
                vals_info = "'" + "', '".join(values[info_columns].astype(str).values.flatten().tolist()) + "'"
                query_insert = """ INSERT into poi(%s) VALUES (%s, ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s),%s),3347),%s);
            """ % (sql_col_string, vals_default, lng, lat, self.config.supply_crs, vals_info)
            else:
                query_insert = """ INSERT into poi(%s) VALUES (%s, ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s),%s),3347));
                """ % (sql_col_string, vals_default, lng, lat, self.config.supply_crs)

            self.execute_query(query_insert, "updated poi")

        # create index for poi table
        self.execute_query("CREATE INDEX idx_poi ON poi USING GIST(point);", "indexed poi")

    def init_demand(self):
        "Create the demand database table"

        if self.centroid == 'weighted':

            self.demand_geo_weight = self.demand_geo_weight.merge(self.demand_pop, on = 'geouid')

            centroid = Centroid(self.demand_geo, self.demand_geo_weight)
            self.centroid_df = centroid.calculate_weighted_centroid()

        else:
            self.demand_geo = self.demand_geo.merge(self.demand_pop, on = 'geouid')

            centroid = Centroid(self.demand_geo)
            self.centroid_df = centroid.calculate_geographic_centroid()

        self.centroid_df.pop = self.centroid_df['pop'].astype(float)
        self.centroid_df.geouid = self.centroid_df['geouid'].astype(int)

        self.centroid_df.reset_index(inplace = True)
        self.centroid_df.rename(columns = {'index': 'id'}, inplace = True)

        centroid_df = self.centroid_df.copy(deep = True)

        centroid_df['centroid'] = [x.wkt for x in centroid_df['centroid']]

        centroid_df = osgeo.ogr.Open(centroid_df.to_json())

        layer = centroid_df.GetLayer(0)

        # create demand table
        query_create = """
        	DROP TABLE IF EXISTS demand;
        	CREATE TABLE demand(
        	id serial PRIMARY KEY,
        	geoUID int,
            pop float,
        	centroid geometry,
        	boundary geometry
        """
        req_columns = ['id', 'geouid', 'pop']
        geo_columns = ['centroid', 'boundary']


        pop_columns = []
        for col in [col for col in self.centroid_df if col.startswith('pop_')]:
            if self.centroid_df[col].dtype == 'O':
                unit = 'text'
            else:
                unit = 'float'

            pop_columns.append(col)
            query_create = query_create + """,  %s %s""" % ('"' + col + '"', unit)

        sql_columns = req_columns + geo_columns + pop_columns
        sql_col_string = '"' + '", "'.join(sql_columns) + '"'

        query_create = query_create + """)"""

        self.execute_query(query_create, "created demand")

        for i in self.centroid_df.index:
            feature = layer.GetFeature(i)
            values = self.centroid_df.loc[i]

            req_values = "'" + "', '".join(values[req_columns].astype(str).values.flatten().tolist()) + "'"
            # req_values = self.centroid_df[req_columns].loc[i] # .astype(str).values.flatten().tolist()
            geometry = feature.GetGeometryRef().ExportToWkt()
            centroid = feature.GetGeometryRef().Centroid().ExportToWkt()

            if len(pop_columns) == 0:
                query_insert = """ INSERT into demand(%s) VALUES (%s, ST_Transform(ST_SetSRID(ST_GeomFromText(%s),%s),3347), ST_Transform(ST_SetSRID(ST_GeomFromText(%s),%s),3347));
                """ % (sql_col_string, req_values, "'" + centroid + "'", self.config.demand_geo_crs, "'" + geometry + "'", self.config.demand_geo_crs)

            else:
                pop_values = "'" + "', '".join(values[pop_columns].astype(str).values.flatten().tolist()) + "'"

                query_insert = """ INSERT into demand(%s) VALUES (%s, ST_Transform(ST_SetSRID(ST_GeomFromText(%s),%s),3347), ST_Transform(ST_SetSRID(ST_GeomFromText(%s),%s),3347), %s);
                """ % (sql_col_string, req_values, "'" + centroid + "'", self.config.demand_geo_crs, "'" + geometry + "'", self.config.demand_geo_crs, pop_values)

            self.execute_query(query_insert, "updated demand")

        # (fuid,ST_Transform(ST_SetSRID(ST_GeomFromText(wkt),self.config.demand_geo_crs),3347),ST_Transform(ST_SetSRID(ST_GeomFromText(centroid),self.config.demand_geo_crs),3347),pop)

        # loop through all features
        '''
        for i in range(layer.GetFeatureCount()):
            # import pdb; pdb.set_trace()
            feature = layer.GetFeature(i) # index value
            fuid = feature.GetField('geouid') # id
            centroid = feature.GetField('centroid') # centroid
            if centroid.startswith("POINT (-n") or centroid.startswith("POINT (n"):
            	centroid = feature.GetGeometryRef().Centroid().ExportToWkt()
            pop = feature.GetField('pop') # population / weight ?
            geometry = feature.GetGeometryRef()
            wkt = geometry.ExportToWkt()
            self.execute_query("INSERT INTO demand (geoUID, boundary, centroid, pop) VALUES (%s,ST_Transform(ST_SetSRID(ST_GeomFromText(%s),%s),3347),ST_Transform(ST_SetSRID(ST_GeomFromText(%s),%s),3347),%s);", "updated demand",
             (fuid, wkt, self.config.demand_geo_crs, centroid, self.config.demand_geo_crs, pop))
            self.db_conn.conn.commit()
        '''

        # create index for demand table
        self.execute_query("CREATE INDEX idx_demand ON demand USING GIST(centroid, boundary);", "indexed demand")

if __name__ == "__main__":
   config = Config('config.json')

   db_schema = InitSchema(config)
