import numpy as np 
import math 
import time
import geopandas as gpd 
import re
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
import openrouteservice as ors

from GeoDataFrame import GeoDataFrame
from CSVDataFrame import CSVDataFrame

class DistanceMatrix:

	def __init__(self, boundary, POI, ORS_client_url, catchment_range, catchment_range_type, catchment_profile, 
					catchment_sleep, dm_metric_type, dm_unit, dm_sleep, ORS_timeout):

		import pdb; pdb.set_trace()
		
		self.web_projection = 'epsg:4326'
		self.SC_projection = 'epsg:3347'

		# ORS variables 
		self.client = ors.Client(key="", base_url = ORS_client_url, timeout = ORS_timeout, retry_over_query_limit = True)

		self.catchment_range = catchment_range
		self.catchment_range_type = catchment_range_type
		self.catchment_profile = catchment_profile
		self.catchment_sleep = catchment_sleep

		self.dm_metric_type = dm_metric_type
		self.dm_unit = dm_unit
		self.dm_sleep = dm_sleep

		# data 
		self.boundary = boundary 

		if self.boundary.get_projection() != self.web_projection:
			self.boundary.change_projection(self.web_projection)

		self.POI = POI

		# set lat / lon columns to point object 

		self.POI = GeoDataFrame(from_file = False, projection = self.web_projection, geometry = self.POI.get_column_by_type('centroid'), df = self.POI)

		import pdb; pdb.set_trace()

		# get result of supply catchment 
		# make into GeoDataFrame ? 

		# filter centroids 

		# get distance matrix 



	def get_supply_catchment(self):
		polygons = []
		ids = []
		locations_list = []

		# IDs of all POIs -- self.POI.df[self.POI.get_column_by_type('ID').get_colname()]
		for i, loc in zip(POI_IDs, POI_locations):
			time.sleep(self.sleep_time)

			call = self.client.isochrones(locations = loc, 
											profile = self.iso_profile, 
											range = catch_range)





	def filter_centroid(self):
		return None

	def dist_m_wrapper(self):
		return None

	def get_dist_m(self):
		return None