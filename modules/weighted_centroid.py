from osgeo import ogr
import numpy as np
import geopandas as gp
from shapely.geometry import MultiLineString, Point
from shapely import wkt
from random import sample
import matplotlib.pyplot as plt
from shapely import wkt

import sys
import pandas as pd


class WeightedCentroid():

	def __init__(self, boundary_sm, boundary_lg):
		self.boundary_sm = boundary_sm
		self.boundary_lg = boundary_lg

	def calculate_weighted_centroid(self):

		if self.boundary_sm.get_column_by_type('weight'):

			# calculating geographic centroids for smallest geography  
			self.boundary_sm.df['centroid'] = self.boundary_sm.df[self.boundary_sm.get_column_by_type('geometry').get_colname()].centroid
			self.boundary_sm.add_col({'colname':'centroid', 'coltype':'centroid', 'coldesc': 'geographic centroid', 'unit': 'geo'})

			# creating lambda function to calculate weighted centroid average
			wm = lambda x: np.ma.average(x, weights = self.boundary_sm.df.loc[x.index, self.boundary_sm.get_column_by_type('weight').get_colname()])

			weighted_cent = pd.DataFrame()

			# calculating weighted latitude and longitude 
			for l in ['lng', 'ltd']:
				colname = 'wtd_' + l
				if l == 'lng':
					self.boundary_sm.df[colname] = self.boundary_sm.df.centroid.apply(lambda p:p.x)
				else:
					self.boundary_sm.df[colname] = self.boundary_sm.df.centroid.apply(lambda p:p.y)

				f = {self.boundary_sm.get_column_by_type('weight').get_colname(): 'sum', colname: wm}

				temp = self.boundary_sm.df.groupby(self.boundary_sm.get_column_by_type('LRG_ID').get_colname()).agg(f)

				if weighted_cent.empty: 
					weighted_cent = temp
				else:
					weighted_cent = pd.merge(weighted_cent.drop(self.boundary_sm.get_column_by_type('weight').get_colname(), axis = 1), temp, left_index = True, right_index = True)

			weighted_cent['weighted_centroid'] = [Point(xy).wkt for xy in zip(weighted_cent.wtd_lng, weighted_cent.wtd_ltd)]

			weighted_cent = weighted_cent[[self.boundary_sm.get_column_by_type('weight').get_colname(), 'weighted_centroid']].reset_index()

			self.boundary_lg.df = pd.merge(self.boundary_lg.df, weighted_cent[[self.boundary_sm.get_column_by_type('LRG_ID').get_colname(), self.boundary_sm.get_column_by_type('weight').get_colname(), 'weighted_centroid']])
			self.boundary_lg.add_col({'colname':'weighted_centroid', 'coltype':'centroid', 'coldesc': 'weighted centroid', 'unit': 'geo'})
			self.boundary_lg.add_col({'colname':self.boundary_sm.get_column_by_type('weight').get_colname(), 'coltype':'weight', 'coldesc':'population', 'unit':'int'})

			# imputing missing values with geographic centroid
			self.boundary_lg.df[self.boundary_lg.get_column_by_type('centroid').get_colname()] = np.where(self.boundary_lg.df[self.boundary_sm.get_column_by_type('weight').get_colname()] == 0, self.boundary_lg.df[self.boundary_lg.get_column_by_type('geometry').get_colname()].centroid, self.boundary_lg.df[self.boundary_lg.get_column_by_type('centroid').get_colname()])

		else:
			self.boundary_lg.df['centroid'] = self.boundary_lg.df[self.boundary_lg.get_column_by_type('geometry').get_colname()].centroid
			self.boundary_lg.add_col({'colname':'centroid', 'coltype':'centroid', 'coldesc': 'geographic centroid', 'unit': 'geo'})

		return self.boundary_lg.df

	def map_weighted_centroid(self, prop, filename_prefix):
		all_IDS = list(set(list(self.boundary_lg.df[self.boundary_lg.get_column_by_type('ID').get_colname()])))
		sample_IDS = sample(all_IDS, round(prop * len(all_IDS)))

		for ID in sample_IDS:
			filename = '{}_{}.png'.format(filename_prefix, ID)

			lg_subset = self.boundary_lg.df[self.boundary_lg.df[self.boundary_lg.get_column_by_type('ID').get_colname()] == ID]

			sm_subset = self.boundary_sm.df[self.boundary_sm.df[self.boundary_sm.get_column_by_type('LRG_ID').get_colname()] == ID]

			base = sm_subset.plot(color = 'white', edgecolor = 'black')

			sm_centroid = sm_subset.set_geometry(self.boundary_sm.get_column_by_type('centroid').get_colname())
			base2 = sm_centroid.plot(ax = base, marker = 'o', color = 'red')

			pops = []
			for x, y, label in zip(sm_centroid.geometry.x, sm_centroid.geometry.y, sm_centroid[self.boundary_sm.get_column_by_type('weight').get_colname()]):
				pops.append(plt.text(x, y, label, fontsize = 8))				
			
			lg_subset['weighted_centroid'] = lg_subset['weighted_centroid'].apply(wkt.loads)	
			lg_centroid = lg_subset.set_geometry(self.boundary_lg.get_column_by_type('centroid').get_colname())
			lg_centroid.plot(ax = base2, marker = 'o', color = 'blue').get_figure().savefig(filename)
