import pandas as pd 
import numpy as np
from osgeo import ogr
import geopandas as gp

from Config import Config
from DataFrame import DataFrame

class GeoDataFrame(DataFrame):

	def __init__(self, filename, filetype, columns, required_columns, projection):
		self.projection = projection
		super().__init__(filename, filetype, columns, required_columns)

	def read_file(self):
		df = gp.read_file(self.name)
		return df

	def set_projection(self):
		self.df.crs = {'init' : self.projection}





