import pandas as pd 
import numpy as np 
from osgeo import ogr
import geopandas as gp

from Column import Column

class DataFrame:

	def __init__(self, filename, filetype, encoding, columns, required_columns):
		self.name = filename
		self.type = filetype
		if encoding == None: 
			self.encoding = 'utf-8'
		else:
			self.encoding = encoding
		self.req_columns = required_columns
		self.columns = self.init_columns(columns)
		self.df = self.read_file()

	def init_columns(self, columns):
		new_columns = []

		for col in self.req_columns:
			new_col = Column(columns[col]['name'], columns[col]['type'], columns[col]['unit'])
			new_columns.append(new_col)

		return new_columns
			 
	def get_column_by_type(self, coltype):
		for column in self.columns:
			if column.get_coltype() == coltype:
				return column

	def get_col_names(self):
		colnames = []
		for column in self.columns:
			colnames.append(column.get_colname())

		return colnames

	def read_file(self):
		if self.type == 'shape':
			df = gp.read_file(self.name)
		elif self.type == 'csv':
			df = pd.read_csv(self.name, encoding = self.encoding)

		return df
	
	def subset_df(self):
		colnames_tokeep = []

		for col in self.req_columns:
			colnames_tokeep.append(self.columns[col])

		self.df = self.df[self.req_columns]



