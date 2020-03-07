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
from WeightedCentroid import WeightedCentroid
from DistanceMatrix import DistanceMatrix
from db import init_logger
import pandas as pd

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
            self.poi = CSVDataFrame(self.config.supply_file, self.config.supply_type, self.config.supply_columns, self.config.required_cols['supply'], self.config.supply_encode)
            self.boundary_lg = GeoDataFrame(self.config.lrg_shapefile, self.config.lrgshape_type, self.config.lrgshape_columns, self.config.required_cols[self.config.lrgshape_type], self.config.lrgshape_projection)
            self.boundary_sm = GeoDataFrame(self.config.sml_shapefile, self.config.smlshape_type, self.config.smlshape_columns, self.config.required_cols[self.config.smlshape_type], self.config.smlshape_projection)
            self.small_pop = CSVDataFrame(self.config.sml_popfile, self.config.smlpop_type, self.config.smlpop_columns, self.config.required_cols[self.config.smlpop_type], self.config.smlpop_encode)
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
            logger.info(f'Successfully {msg} database table')
        except Exception as e:
            logger.error(f'Unsuccessfully {msg} database table: {e}')

    def create_schema(self):
        "Create each PostgreSQL database table"

        self.init_demand()
        self.init_poi()
        self.init_distance_matrix()

    def init_distance_matrix(self, profiles=["car"]):
        "Create distance_matrix database table"
        for profile in profiles:
            # TO DO: this will need to change based on different profiles
            DM = DistanceMatrix(self.poi, self.calculated_centroid, self.config.ORS_client, self.config.iso_catchment_range,
                self.config.iso_catchment_type, self.config.iso_profile, self.config.iso_sleep_time, self.config.dm_metric,
                self.config.dm_unit, self.config.dm_sleep_time, self.config.ORS_timeout)

            # TO DO: distance_matrix return should be of this structure:
            # geouid, poiuid ...

            # for testing rest of script
            #distance_matrix = pd.read_csv("C:/Code/pos-accessibility/pos-accessibility-app/data/distance_matrix_60min.csv", encoding = "latin-1")

            # TO DO: update query for different distance_matrix_* based on mode of transportation (will have to update config.json)
            query_create = """
                        DROP TABLE IF EXISTS distance_matrix_%s;
                        CREATE TABLE distance_matrix_%s(
                        id serial PRIMARY KEY""" % (profile, profile)

            # loop through all columns to build query statement to create the distance_matrix_* table
            # TO DO: consider different data type?
            for col in DM.distance_matrix.columns.values:
                if col == DM.distance_matrix.columns.values[-1]:
                    query_create += ", " + col + " text)"
                else:
                    query_create += ", " + col + " text"

            self.execute_query(query_create, "created distance_matrix_" + profile)

            columns = ", ".join(DM.distance_matrix.columns.values.tolist()) # list of columns as a string
            rows = DM.distance_matrix.to_numpy().tolist() # list of rows

            # for each row in distance matrix
            for i in DM.distance_matrix.index:
                rows[i] = [str(value) for value in rows[i]] # cast each row value as string
                values = "'" + "', '".join(rows[i]) + "'" # store a row's values into a list as a string

                # insert row into database table
                query_insert = """ INSERT into distance_matrix_%s (%s) VALUES (%s);
                """ % (profile, columns, values)
                self.execute_query(query_insert, "updated distance_matrix")

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
            point geometry(POINT,3347),
            supply int
        """

        # TO DO: ask Chelsea about LRD_ID

        sql_columns = ['id', 'geouid', 'lrg_id', 'point', 'supply']

        # create POI DataFrame object

        self.poi.df.reset_index(inplace = True)

        # TO DO: CMAUID is hard coded?

        self.poi.df.CMAUID = np.where(self.poi.df.CMAUID == ' ', None, self.poi.df.CMAUID)

        for col in self.poi.get_column_by_type('supply_info'):
            col_name = 'info_' + col.get_colname().lower().replace(" ", "_")
            unit = col.get_sql_colunit()

            sql_columns.append(col_name)
            query_create = query_create + """,  %s %s""" % (col_name, unit)

        query_create = query_create + """)"""

        self.execute_query(query_create, "created poi")

        sql_col_string = '"' + '", "'.join(sql_columns) + '"'

        for i in self.poi.df.index:
            values = self.poi.df.loc[i].astype(str).values.flatten().tolist()

            # TO DO: remove hardcoding, base it off config file (need to ask Chelsea still what each key/value means)
            vals_default = "'" + "', '".join(values[0:3]) + "'"
            lat = values[3]
            lng = values[4]
            vals_info = "'" + "', '".join(values[5:]) + "'"

            query_insert = """ INSERT into poi(%s) VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s),3347),%s);
            """ % (sql_col_string, vals_default, lng, lat, vals_info)

            self.execute_query(query_insert, "updated poi")

        # create index for poi table
        self.execute_query("CREATE INDEX idx_poi ON poi USING GIST(point);", "indexed poi")

    def init_demand(self):
        "Create the demand database table"

        self.boundary_sm.merge_DataFrame(self.small_pop)

        centroid = WeightedCentroid(self.boundary_lg, self.boundary_sm)
        centroid.calculate_centroid()
        self.calculated_centroid = centroid.boundary_lg
        centroid_df = self.calculated_centroid.df.copy(deep = True)
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
        self.execute_query(query_create, "created demand")

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
            self.execute_query("INSERT INTO demand (geoUID, boundary, centroid, pop) VALUES (%s,ST_SetSRID(ST_GeomFromText(%s),3347),%s,%s);", "updated demand", (fuid,wkt,centroid,pop))
            self.db_conn.conn.commit()

        # create index for demand table
        self.execute_query("CREATE INDEX idx_demand ON demand USING GIST(centroid, boundary);", "indexed demand")

if __name__ == "__main__":
   config = Config('config.json')

   db_schema = InitSchema(config)
