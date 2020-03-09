import pandas as pd 
import numpy as np
from osgeo import ogr
import geopandas as gp

from Config import Config
from DataFrame import DataFrame

class GeoDataFrame(DataFrame):

	def __init__(self, filename = None, filetype = None, columns = None, required_columns = None, 
				projection = None, geometry = None, df= None, from_file = True):
		
		if from_file:
			self.projection = projection
			super().__init__(filename, filetype, columns, required_columns)
			self.set_projection()
		else:
			self.projection = projection

			self.name = df.name
			self.type = df.type
			self.req_columns = df.req_columns
			self.columns = df.columns 

			self.df = gp.GeoDataFrame(df.df, geometry = df.df[geometry.get_colname()], crs = {'init': projection})

	def read_file(self):
		""" Read in shape file """ 
		df = gp.read_file(self.name)
		return df

	def set_projection(self):
		""" Change geometry projection """
		self.df.crs = {'init' : self.projection}

	def get_projection(self):
		return self.projection

	def change_projection(self, new_projection):
		self.df = self.df.to_crs({'init':new_projection})

		self.projection = new_projection






