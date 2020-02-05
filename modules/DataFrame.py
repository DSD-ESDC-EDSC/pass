import pandas as pd 
import numpy as np 

from Column import Column

class DataFrame:

	def __init__(self, filename, filetype, columns, required_columns, skinny = True):
		self.name = filename
		self.type = filetype
		self.req_columns = required_columns
		self.df = self.read_file()
		self.columns = self.init_columns(columns)
		self.conform_col_units()
		if skinny:
			self.shave_df()


	def init_columns(self, columns):
		new_columns = []

		for col in self.req_columns:
			try: 
				unit = self.df[columns[col]['name']].dtype
			except: 
				print('Column not found in data.')
				import pdb; pdb.set_trace()

			try:
				new_col = Column(columns[col]['name'], columns[col]['type'], columns[col]['descr'], unit)
				new_columns.append(new_col)
			except:
				print('Please ensure you have all required columns in config file.')

		return new_columns

	def shave_df(self):
		cols_to_keep = self.get_col_names()

		self.df = self.df[cols_to_keep]

	def conform_col_units(self):
		for col in self.columns:
			# get column unit
			defined_unit = col.get_coldesc()
			current_unit = col.get_colunit()

			if current_unit == 'O' or current_unit == 'str':
				if defined_unit == 'O' or defined_unit == 'str':
					return
				elif defined_unit == 'int' or defined_unit == 'float':
					self.df[col.get_colname()]= self.df[col.get_colname()].astype(float)
					current_unit = defined_unit
			elif current_unit == 'int' or current_unit == 'float':
				if defined_unit == 'int' or defined_unit == 'float':
					return
				elif defined_unit == 'str' or defined_unit == 'O':
					self.df[col.get_colname()] = self.df[col.get_colname()].astype(str)
					current_unit = defined_unit

	def get_columns(self):
		return self.columns
			 
	def get_column_by_type(self, coltype):
		for column in self.columns:
			if column.get_coltype() == coltype:
				return column

	def get_column_by_name(self, colname):
		for column in self.columns:
			if column.get_colname() == colname:
				return column

	def get_col_names(self):
		colnames = []
		for column in self.columns:
			colnames.append(column.get_colname())

		return colnames

	def get_col_types(self):
		coltypes = []
		for column in self.columns:
			coltypes.append(column.get_coltype())

		return coltypes
	
	def subset_df(self):
		colnames_tokeep = []

		for col in self.req_columns:
			colnames_tokeep.append(self.columns[col])

		self.df = self.df[self.req_columns]

	def remove_col(self, col_toremove):
		'''
		** ONLY EVERY CALLED BY ADD COL 
		'''
		self.columns.remove(col_toremove)

	def add_col(self, new_col, override = False):
		if type(new_col) == dict:
			new_col = Column(new_col['colname'], new_col['coltype'], new_col['coldesc'], new_col['unit'])
			
		if override:
			self.remove_col(self.get_column_by_type(new_col.get_coltype()))
			self.columns.append(new_col)

		else:
			if new_col.get_coltype() not in (self.get_col_types()):
				self.columns.append(new_col)

	def merge_DataFrame(self, df2, override = False):
		# determining if columns are of the same type, if they are not, 


		# if self.get_column_by_type('ID').get_colunit() != df2.get_column_by_type('ID').get_colunit():
		# 	df2.df[df2.get_column_by_type('ID').get_colname()] = df2.df[df2.get_column_by_type('ID').get_colname()].astype(self.get_column_by_type('ID').get_colunit())

		# actual merging two dataframes
		self.df = self.df.merge(df2.df, left_on = self.get_column_by_type('ID').get_colname(), right_on = df2.get_column_by_type('ID').get_colname(), how = 'left')

		# adding column objects to self 
		for col in df2.get_columns():
			self.add_col(col, False)


