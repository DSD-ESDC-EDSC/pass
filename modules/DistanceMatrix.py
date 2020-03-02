import numpy as np 
import math 
import time
import geopandas as gpd 
import re
from shapely.geometry import Polygon, Point
import shapely
# import matplotlib.pyplot as plt
import openrouteservice as ors

from GeoDataFrame import GeoDataFrame
from CSVDataFrame import CSVDataFrame

class DistanceMatrix:

	def __init__(self, boundary, POI, weighted_centroid, ORS_client_url, catchment_range, catchment_range_type, catchment_profile, 
					catchment_sleep, dm_metric_type, dm_unit, dm_sleep, ORS_timeout):
		
		self.web_projection = 'epsg:4326'
		self.SC_projection = 'epsg:3347'

		# ORS variables 
		self.client = ors.Client(key="", base_url = ORS_client_url, timeout = ORS_timeout, retry_over_query_limit = True)

		self.client = ors.Client(key="", base_url = 'http://10.54.61.201:8080/ors', timeout = 500, retry_over_query_limit = True)

		self.catchment_range = catchment_range
		self.catchment_range_type = catchment_range_type
		self.catchment_profile = catchment_profile
		self.catchment_sleep = catchment_sleep

		self.dm_metric_type = dm_metric_type
		self.dm_unit = dm_unit
		self.sleep_time = dm_sleep

		# data 
		self.boundary = boundary 

		if self.boundary.get_projection() != self.web_projection:
			self.boundary.change_projection(self.web_projection)

		self.weighted_centroid = weighted_centroid

		self.weighted_centroid.df[self.weighted_centroid.get_column_by_type('centroid').get_colname()] = self.weighted_centroid.df[self.weighted_centroid.get_column_by_type('centroid').get_colname()].map(shapely.wkt.loads)

		self.weighted_centroid.df.set_geometry(self.weighted_centroid.get_column_by_type('centroid').get_colname(), inplace = True)

		if self.weighted_centroid.get_projection() != self.web_projection:
			self.weighted_centroid.change_projection(self.web_projection)

		self.POI = POI

		self.POI.df['POI'] = [Point(xy) for xy in zip(self.POI.df[self.POI.get_column_by_type('longitude').get_colname()], self.POI.df[self.POI.get_column_by_type('latitude').get_colname()])]
		self.POI.add_col({'colname': 'POI', 'coltype': 'geometry', 'coldesc': 'POI lat/lon', 'unit': 'geo'})

		self.POI = GeoDataFrame(from_file = False, projection = self.web_projection, geometry = self.POI.get_column_by_type('geometry'), df = self.POI)

		self.ISO = self.get_supply_catchment()

		self.in_iso = self.weighted_centroid.df

		self.filter_centroids()
		
		import pdb; pdb.set_trace()

		# get distance matrix 



	def get_supply_catchment(self):
		polygons = []
		ids = []
		locations_list = []

		# not_found_i = []
		# not_found_locations = []

		# import pdb; pdb.set_trace()

		# IDs of all POIs -- self.POI.df[self.POI.get_column_by_type('ID').get_colname()]
		for i, loc in zip(self.POI.df[self.POI.get_column_by_type('ID').get_colname()], zip(self.POI.df[self.POI.get_column_by_type('longitude').get_colname()], self.POI.df[self.POI.get_column_by_type('latitude').get_colname()])):
			time.sleep(self.catchment_sleep)
			try: 
				call = self.client.isochrones(locations = [loc], profile = self.catchment_profile, range = [self.catchment_range])

				iso_geometry = call['features'][0]['geometry']

				coords = np.array(iso_geometry['coordinates'][0])

				polygon_geom = Polygon(coords)

				polygons.append(polygon_geom)

				ids.append(i)

				locations_list.append(loc)

			except:
				# not_found_i.append(i)
				# not_found_locations.append(loc)
				print('unable to build isochrone for loc ', loc, '. It will not be included in results.')

		polygon = gpd.GeoDataFrame(index = ids, crs = self.web_projection, geometry = polygons)
		polygon['id'] = ids
		polygon['location'] = locations_list

		return polygon

	def filter_centroids(self):

		for index, row in self.ISO.iterrows():
			self.weighted_centroid.df['POS_' + str(row['id'])] = self.weighted_centroid.df[self.weighted_centroid.get_column_by_type('centroid').get_colname()].map(lambda x: True if row.geometry.contains(x) == True else False)

	def dist_m_wrapper(self):
		# get list of POS IDs 

		POS_IDs = self.POI.df[self.POI.get_column_by_type('ID').get_colname()].values.tolist()

		for posID in POS_IDs:
			colname = 'POS_' + str(posID)
			pos = self.ISO[self.ISO] # what columns are in ISO ? need to filter by id variable

			centroid_subset = self.weighted_centroid[self.weighted_centroid[colname]]
			dm_name = 'POS' + str(posID) + '_' + self.dm_metric_type

			if len(centroid_subset.index) > 0:
				result = self.get_dist_m(pos)
			else:
				centroid_subset[dm_name] = np.nan
				result = centroid_subset
			result.rename(column = {self.dm_metric_type:dm_name}, inplace = True)
			self.weighted_centroid.df = centroid_df.merge(result[[self.weighted_centroid.get_column_by_type('ID').get_colname(), dm_name]], how = 'left', on = self.weighted_centroid.get_column_by_type('ID').get_colname())
			self.weighted_centroid.df.drop(labels = colname, axis = 1, inplace = True)

	def get_dist_m(self, pos):
		# client
		# df
		# pos
		# lat_col_name
		# lon_col_name
		# distance_metric
		# distance_unit
		# sleep time 

		num_groups = math.ceil(len(df) / 1000)
		all_result = []

		for min_df in np.array_split(self.weighted_centroid.df, num_groups):

			centroid_list = min_df[[self.weighted_centroid.get_column_by_type('longitude').get_colname(), self.weighted_centroid.get_column_by_type('latitude').get_colname()]].values.tolist()

			all_locations = pos + centroid_list

			call = self.client.distance_matrix(locations = all_locations, 
												destinations = [0], 
												profile = 'driving-car', 
												metrics = [self.dm_metric_type], 
												units = self.dm_unit)

			result = call[self.dm_metric_type + 's']

			result.pop(0)

			result = sum(result, [])

			all_result.append(result)

		all_result = sum(all_result, [])

		self.weighted_centroid.df[self.dm_metric_type] = all_result