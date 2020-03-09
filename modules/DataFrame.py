import pandas as pd 
import numpy as np 
import sys 

from Column import Column

class DataFrame:

	def __init__(self, filename, filetype, columns, required_columns, skinny = True):
		self.name = filename
		self.type = filetype
		self.req_columns = required_columns
		self.df = self.read_file()
		self.columns = self._init_req_columns(columns)
		self._conform_col_units()
		self.columns = self.columns + self._init_opt_columns(columns)
		if skinny:
			self._shave_df()
		self.df = self.prepare_DataFrame()


	def _init_req_columns(self, columns):
		""" Creates column objects for each column required by dataframe type. Throws error if a required column is not found in data. """

		new_columns = []

		# looping through required columns
		for col in self.req_columns:
			'''
			try: 
				# getting the variable type of the column 
				unit = self.df[columns[col]['name']].dtype
			except: 
				# exit if the column isn't found in the data 
				print(col, ' column not found in data.')
				sys.exit(1)
			'''
			try:
				# creating new column object 
				new_col = Column(columns[col]['name'], columns[col]['type'], columns[col]['descr'], columns[col]['unit'])
				new_columns.append(new_col)
			except:
				print('Please ensure you have all required columns in config file.')
				sys.exit(1)

		return new_columns

	def _init_opt_columns(self, columns):
		""" Creates column objects for all optional columns. """
		new_columns = []

		# looping through all user defined columns
		for col in columns:
			if col not in self.req_columns:
				unit = self.df[columns[col]['name']].dtype
				if unit == 'O':
					self.preprocess_opt_columns(columns[col]['name'])
				new_col = Column(columns[col]['name'], columns[col]['type'], columns[col]['descr'], unit)
				new_columns.append(new_col)

		return new_columns

	def preprocess_opt_columns(self, col):
		""" preprocessing text columns to remove quotations """ 
		if self.df[col].dtype == 'O':
			self.df[col] = self.df[col].str.replace("'", " ")
			self.df[col] = self.df[col].str.replace('"', ' ')

	def _shave_df(self):
		""" Subsets df to only columns defined by user """
		cols_to_keep = self.get_col_names()

		self.df = self.df[cols_to_keep]

	def _conform_col_units(self):
		""" Used for all required columns, checks that column variable types match user defined variable types. 
			Converts column to user defined type if not already conformed """
		for col in self.columns:
			# get user defined unit and actual column unit
			defined_unit = col.get_colunit()
			current_unit = self.df[col.get_colname()].dtype

			# ensuring defined and actual column units are the same, changing them if not 
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
		""" Returns list of column objects """
		return self.columns
			 
	def get_column_by_type(self, coltype):
		""" Returns all column objects matching specified column type """
		columns_toreturn = []

		for column in self.columns:
			if column.get_coltype() == coltype:
				columns_toreturn.append(column)

		if len(columns_toreturn) ==1:
			return columns_toreturn[0]
		elif len(columns_toreturn) > 1:
			return columns_toreturn
		else:
			return None

	def get_column_by_name(self, colname):
		""" Returns all column objects matching specified column name """
		columns_toreturn = []
		for column in self.columns:
			if column.get_colname() == colname:
				columns_toreturn.append(column)

		if len(columns_toreturn) == 1:
			return columns_toreturn[0]
		elif len(columns_toreturn) > 1:
			return columns_toreturn
		else:
			return None

	def get_col_names(self):
		""" Returns names of all column objects """
		colnames = []
		for column in self.columns:
			colnames.append(column.get_colname())

		return colnames

	def get_col_types(self):
		""" Returns types of all column objects """
		coltypes = []
		for column in self.columns:
			coltypes.append(column.get_coltype())

		return coltypes

	def get_col_descs(self):
		""" Returns descriptions of all column objects """
		coldescs = []
		for column in self.columns:
			coldescs.append(column.get_coldesc())

		return coldescs		

	def get_col_units(self):
		""" Returns units of all column objects """
		colunits = []
		for column in self.columns:
			colunits.append(column.get_colunit())

		return colunits		

	def remove_col(self, col_toremove):
		""" Removes column object. Only ever called by add_col """
		self.columns.remove(col_toremove)

	def add_uniform_col(self, new_col_name):
		""" Adding column of 1s to df """
		self.df[new_col_name] = 1
		new_col = self.add_col({'colname': new_col_name, 'coltype':new_col_name, 'coldesc': 'uniform ' + new_col_name, 'unit': 'int'})

	def add_col(self, new_col, override = False):
		""" Adds new column object to DataFrame. """
		if type(new_col) == dict:
			new_col = Column(new_col['colname'], new_col['coltype'], new_col['coldesc'], new_col['unit'])
			
		if override:
			# replace column in current DataFrame object with df2 column (if there are overlapping column types) 	
			self.remove_col(self.get_column_by_type(new_col.get_coltype()))
			self.columns.append(new_col)

		else:
			# only add column object from df2 if there does not exist a column object in current df of same type
			if new_col.get_coltype() not in (self.get_col_types()):
				self.columns.append(new_col)

	def merge_DataFrame(self, df2, override = False):
		""" Merges df2 into current DataFrame object """

		# merging dataframes on ID variables 
		self.df = self.df.merge(df2.df, left_on = self.get_column_by_type('ID').get_colname(), right_on = df2.get_column_by_type('ID').get_colname(), how = 'left')

		for col in df2.get_columns():
			self.add_col(col, False)

	def prepare_DataFrame(self):
		""" adds supply / demand term to table if necessary. Orders columns for easy writing to sql db """ 

		final_column_order = []

		for col_type in self.req_columns:
			final_column_order.append(self.get_column_by_type(col_type).get_colname())

		if self.type == 'supply':
			# check that there's a supply column, if not, add one
			if not self.get_column_by_type('supply'):
				self.add_uniform_col('supply')

			final_column_order.append(self.get_column_by_type('supply').get_colname())
		elif self.type == 'demand':
			if not self.get_column_by_type('demand'):
				self.add_uniform_col('demand')

			final_column_order.append(self.get_column_by_type('demand').get_colname())

		additional_columns = set(self.get_col_names()).difference(set(final_column_order))

		final_column_order += additional_columns

		return self.df[final_column_order]

