from osgeo import ogr
import numpy as np
import geopandas as gp
from shapely.geometry import MultiLineString, Point
from shapely import wkt
from random import sample
# import matplotlib.pyplot as plt
from shapely import wkt

import sys
import pandas as pd

import utils

class Centroid():

	def __init__(self, demand_geo, demand_geo_weight = None):
		self.demand_geo = demand_geo
		if demand_geo_weight is not None: 
			self.demand_geo_weight = demand_geo_weight
		

	def calculate_weighted_centroid(self):
		""" Calculates the centroid of boundary_lg, weighted by weight column of boundary_sm.
			If no weight column is found, calculates geographic centroid. """

		# calculating geographic centroids for smallest geography
		self.demand_geo_weight['centroid'] = self.demand_geo_weight['geometry'].centroid
		
		print(self.demand_geo_weight['centroid'])

		# creating lambda function to calculate weighted centroid average
		wm = lambda x: np.ma.average(x, weights = self.demand_geo_weight.loc[x.index, 'pop_Total'])

		weighted_cent = pd.DataFrame()

		# calculating weighted latitude and longitude
		for l in ['lng', 'ltd']:
			colname = 'wtd_' + l

			if l == 'lng':
				self.demand_geo_weight[colname] = self.demand_geo_weight.centroid.apply(lambda p:p.x)
				print(self.demand_geo_weight[colname])
			else:
				self.demand_geo_weight[colname] = self.demand_geo_weight.centroid.apply(lambda p:p.y)

			f = {'pop_Total': 'sum', colname: wm}

			temp = self.demand_geo_weight.groupby('lrg_id').agg(f)

			if weighted_cent.empty:
				weighted_cent = temp
			else:
				weighted_cent = pd.merge(weighted_cent.drop('pop_Total', axis = 1), temp, left_index = True, right_index = True)
		
		print(weighted_cent)
		# zipping weighted lat / lon
		weighted_cent['centroid'] = utils.create_point(weighted_cent.wtd_lng, weighted_cent.wtd_ltd)

		weighted_cent = weighted_cent[['pop_Total', 'centroid']].reset_index()

		# merging weighted centroid back into boundary_lg
		self.demand_geo = pd.merge(self.demand_geo, weighted_cent[['lrg_id', 'pop_Total', 'centroid']], left_on = 'geouid', right_on = 'lrg_id')
		self.demand_geo.drop('lrg_id_y', axis = 1, inplace = True)
		self.demand_geo.rename(columns = {'lrg_id_x':'lrg_id'}, inplace = True)

		# imputing missing values with geographic centroid
		self.demand_geo['centroid'] = np.where(self.demand_geo.pop_Total == 0, self.demand_geo.geometry.centroid, self.demand_geo.centroid)
		# self.boundary_lg.df['weighted_centroid'] = [x.wkt for x in self.boundary_lg.df.weighted_centroid]

		return self.demand_geo

	def calculate_geographic_centroid(self):
		self.demand_geo['centroid'] = self.demand_geo['geometry'].centroid

		return self.demand_geo

	def map_weighted_centroid(self, prop, filename_prefix):
		""" Function to map sample centroids. Mostly for spot checking. """
		all_IDS = list(set(list(self.boundary_lg.df[self.boundary_lg.get_column_by_type('ID').get_colname()])))
		sample_IDS = sample(all_IDS, round(prop * len(all_IDS)))

		for ID in sample_IDS:
			filename = '{}_{}.png'.format(filename_prefix, ID)

			# subsetting large and small boundary dfs by sample ID
			lg_subset = self.boundary_lg.df[self.boundary_lg.df[self.boundary_lg.get_column_by_type('ID').get_colname()] == ID]

			sm_subset = self.boundary_sm.df[self.boundary_sm.df[self.boundary_sm.get_column_by_type('LRG_ID').get_colname()] == ID]

			# plotting base
			base = sm_subset.plot(color = 'white', edgecolor = 'black')

			# plotting sm_subset geographic centroids
			sm_centroid = sm_subset.set_geometry(self.boundary_sm.get_column_by_type('centroid').get_colname())
			base2 = sm_centroid.plot(ax = base, marker = 'o', color = 'red')

			# adding population to map
			pops = []
			for x, y, label in zip(sm_centroid.geometry.x, sm_centroid.geometry.y, sm_centroid[self.boundary_sm.get_column_by_type('pop').get_colname()]):
				pops.append(plt.text(x, y, label, fontsize = 8))

			# plotting lg_subset weighted centroid
			lg_subset['weighted_centroid'] = lg_subset['weighted_centroid'].apply(wkt.loads)
			lg_centroid = lg_subset.set_geometry(self.boundary_lg.get_column_by_type('centroid').get_colname())
			lg_centroid.plot(ax = base2, marker = 'o', color = 'blue').get_figure().savefig(filename)
