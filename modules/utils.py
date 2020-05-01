import pandas as pd 
import geopandas as gp
import numpy as np 
import sys 

from shapely.geometry import MultiLineString, Point

def read_file(filename, filetype, columns, req_columns, encoding):
	if filetype == 'shape':
		# read in shape file 
		crs = encoding 
		df = gp.read_file(filename)
		df.crs = {'init': 'epsg:' + str(crs)}
	else:
		# read in csv file 
		df = pd.read_csv(filename, encoding = encoding)

	# rename all (required) columns to be their types 
	df = init_columns(df, filetype, columns, req_columns)
	# columns_torename_info = init_open_columns(df, columns, req_columns)
	# any specified columns that are not required, get prepended info_ 
	# cast all columns to have same type as what was passed in 

	return df


def init_columns(df, df_type, columns, req_columns):
	""" Creates column objects for each column required by dataframe type. Throws error if a required column is not found in data. """

	columns_torename = {}
	opt_columns_torename = {}

	if set(req_columns).issubset(columns.keys()):
		for col in columns:
			if col in req_columns:
				# creating new column object 
				columns_torename[columns[col]['name']] = columns[col]['type']
			else:
				if df_type == 'demand':
					preffix = 'pop_'
				if df_type == 'supply':
					if columns[col]['desc'] == 'info':
						preffix = 'info_'
					if columns[col]['desc'] == 'capacity':
						preffix = 'capacity_'
					if columns[col]['desc'] == 'supply':
						preffix = 'supply_'
				opt_columns_torename[columns[col]['name']] = preffix + columns[col]['type']

			df[columns[col]['name']] = conform_col_units(df[columns[col]['name']], columns[col])
	else:
		print('Please ensure you have all required columns in config file.')
		sys.exit(1)

	columns_torename.update(opt_columns_torename)

	df.rename(columns = columns_torename, inplace = True)

	return df[columns_torename.values()]

def conform_col_units(df_series, column):
	""" Used for all required columns, checks that column variable types match user defined variable types. 
		Converts column to user defined type if not already conformed """
		# get user defined unit and actual column unit
	defined_unit = column['unit']
	current_unit = df_series.dtype

	# ensuring defined and actual column units are the same, changing them if not 
	if current_unit == 'O' or current_unit == 'str':
		if defined_unit == 'int' or defined_unit == 'float':
			df_series = df_series.astype(float)

	elif current_unit == 'int' or current_unit == 'float':			
		if defined_unit == 'str' or defined_unit == 'O':
			df_series = df_series.astype(str)

	if df_series.dtype =='str' or df_series.dtype == 'O':
		df_series = preprocess_str(df_series)

	return df_series

def preprocess_str(series):
	series = series.str.replace("'", " ")
	series = np.where(series == ' ', None, series)

	return series

def create_point(lon_col, lat_col):
	return [Point(xy) for xy in zip(lon_col, lat_col)]
