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

	def __init__(self, POI, weighted_centroid, ORS_client_url, catchment_range, catchment_range_type, catchment_profile,
					catchment_sleep, dm_metric_type, dm_unit, dm_sleep, ORS_timeout):

		self.web_projection = 4326
		self.SC_projection = 3347

		self.crs_preffix = 'epsg:'

		# ORS variables
		self.client = ors.Client(key="", base_url = ORS_client_url, timeout = ORS_timeout, retry_over_query_limit = True)

		self.catchment_range = catchment_range
		self.catchment_range_type = catchment_range_type
		self.catchment_profile = catchment_profile
		self.catchment_sleep = catchment_sleep

		self.dm_metric_type = dm_metric_type
		self.dm_unit = dm_unit
		self.sleep_time = dm_sleep

		# data
		self.weighted_centroid = weighted_centroid

		# TO DO: Update weighted_centroid is that it can either be a data frame from db or from self

		self.weighted_centroid = self.weighted_centroid.set_geometry('centroid')

		if self.weighted_centroid.crs != self.crs_preffix + str(self.web_projection):
			self.weighted_centroid.to_crs({'init': self.crs_preffix + str(self.web_projection)}, inplace = True)

		self.weighted_centroid['latitude'] = self.weighted_centroid.geometry.y
		self.weighted_centroid['longitude'] = self.weighted_centroid.geometry.x

		self.POI = POI

		self.POI['POI'] = [Point(xy) for xy in zip(self.POI.longitude, self.POI.latitude)]

		self.POI = self.POI.set_geometry('POI')
		self.POI.crs = {'init': self.crs_preffix + str(self.web_projection)}

		# calculate catchment area for each POS
		self.ISO = self.get_supply_catchment()

		self.in_iso = self.weighted_centroid

		# filter centroids included in each catchment
		self.filter_centroids()

		# get distance matrix
		self.dist_m_wrapper()

		import pdb; pdb.set_trace()

		pos_cols = [col for col in self.weighted_centroid if col.startswith('POS')]

		cols_tokeep = [self.weighted_centroid.get_column_by_type('ID').get_colname()] + pos_cols

		self.distance_matrix = self.weighted_centroid[cols_tokeep]

	def get_supply_catchment(self):
		polygons = []
		ids = []
		locations_list = []

		for i, loc in zip(self.POI.geouid, zip(self.POI.longitude, self.POI.latitude)):
			time.sleep(self.catchment_sleep)
			try:
				# import pdb; pdb.set_trace()

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

		polygon = gpd.GeoDataFrame(index = ids, crs = self.crs_preffix + str(self.web_projection), geometry = polygons)
		polygon['id'] = ids
		polygon['location'] = locations_list

		return polygon

	def filter_centroids(self):

		for index, row in self.ISO.iterrows():
			self.weighted_centroid['poi_' + str(row['id'])] = self.weighted_centroid['centroid'].map(lambda x: True if row.geometry.contains(x) == True else False)

	def dist_m_wrapper(self):
		# get list of POS IDs

		import pdb; pdb.set_trace()

		POS_IDs = [int(col[4:]) for col in self.weighted_centroid if col.startswith('poi')]

		for posID in POS_IDs:
			colname = 'poi_' + str(posID)
			pos = list(self.ISO[self.ISO.id == posID].iloc[0]['location'])

			centroid_subset = self.weighted_centroid[self.weighted_centroid[colname]]
			dm_name = 'poiuid_' + str(posID) 

			if len(centroid_subset.index) > 0:
				result = self.get_dist_m(pos, centroid_subset, 'latitude', 'longitude')
			else:
				centroid_subset[dm_name] = None
				result = centroid_subset

			result.rename(columns = {self.dm_metric_type:dm_name}, inplace = True)
			self.weighted_centroid = self.weighted_centroid.merge(result[['geouid', dm_name]], how = 'left', on = 'geouid')
			self.weighted_centroid.drop(labels = colname, axis = 1, inplace = True)


	def get_dist_m(self, pos, centroid_subset, lat, lon):

		num_groups = math.ceil(len(centroid_subset) / 1000)
		all_result = []

		for min_df in np.array_split(centroid_subset, num_groups):

			centroid_list = min_df[[lon, lat]].values.tolist()

			all_locations = [pos] + centroid_list

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

		centroid_subset[self.dm_metric_type] = all_result

		return centroid_subset
