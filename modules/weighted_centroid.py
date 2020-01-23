from osgeo import ogr
import numpy as np
import geopandas as gp
from shapely.geometry import MultiLineString, Point
from shapely import wkt
from random import sample
#mport matplotlib.pyplot as plt

import sys
import pandas as pd

def subset_df(df, cols_to_keep):
	'''
	Helper function to subset dataframe
	Inputs: df- dataframe to subset
			cols_to_keep- list of column names to keep in dataframe
	Returns: subsetted dataframe
	'''
	if cols_to_keep != None:
		df = df[cols_to_keep]

	return df

def rename_cols(df, new_col_names):
	'''
	Helper function to rename columns
	Input: df- dataframe
		   new_col_names- list of new column names, length of new columns must match df shape
	Returns: df with new names
	'''
	if new_col_names != None:
		df.columns = new_col_names

	return df

def calculate_centroid(boundary_sm, boundary_lg, uid, weight):
	'''
	Function to calculated population weighted centroids. Takes in a dataframe and column names for the
	grouping variable, local geometry, and population (or something else) weights. Returns a dataframe with new columns
	Inputs: boundary_sm - geodataframe of small boundary file, must have a weight column already joined to file
		boundary_lg - geodataframe of large boundary file
		uid - boundary_lg unique id column name
		weight - boundary_small weight column name (e.g., population)
	Returns: boundary_lg
	'''

	if (weight):
	    # calculates local centroid and creates separate lat/lon columns
		boundary_sm['centroid'] = boundary_sm['geometry'].centroid
		boundary_sm[weight] = boundary_sm[weight].dropna().astype(int)

		# TO DO: UPDATE THIS TO REFLECT OGR CENTROID, NOT GEODATAFRAME
		boundary_sm['wtd_lng'] = boundary_sm.centroid.apply(lambda p: p.x)
		boundary_sm['wtd_ltd'] = boundary_sm.centroid.apply(lambda p: p.y)

		# define a lambda function to compute the weighted mean
		wm = lambda x: np.ma.average(x, weights = boundary_sm.loc[x.index, weight])

		# defining aggregate functions and applying them to each region
		f_lng = {weight: ['sum'], 'wtd_lng': wm }
		f_ltd = {weight: ['sum'], 'wtd_ltd': wm }

		temp_lng = boundary_sm.groupby([uid]).agg(f_lng)
		temp_ltd = boundary_sm.groupby([uid]).agg(f_ltd)

		# merging lat/lon and cleanup
		# TO DO RENAME THESE / REDUCE SCRIPTING FOR THIS
		agg_merge = pd.merge(temp_lng, temp_ltd, left_index=True, right_index=True)
		agg_merge = agg_merge[["wtd_lng", "wtd_ltd"]]
		agg_merge.columns = ["wtd_lng", "wtd_ltd"]
		agg_merge = agg_merge[['wtd_lng', 'wtd_ltd']]
		final = pd.merge(boundary_lg, agg_merge.reset_index(), on = uid)
		centroid_geom = [Point(xy).wkt for xy in zip (final.wtd_lng, final.wtd_ltd)]
		final = final.drop(["wtd_lng", "wtd_ltd"], axis=1)
		final['centroid'] = centroid_geom
		return final

	else:
		boundary_lg['centroid'] = boundary_lg['geometry'].centroid
		return boundary_lg

def impute_missing_centroid(df, da_df, DAUID, da_geometry):
	'''
	Imputing centroid lat/lon for DAs which have no population. Instead of DB population weighted centroid, these areas
	will have the basic geographical centroid
	Inputs: df- table of already calculated centroids
			da_df- table at DA level
			DAUID- ID variable name for DA
			da_geometry- variable name of DA geometry column
	Returns: df with missing centroids filled
	'''
	da_df['centroid_lat'] = da_df[da_geometry].centroid.apply(lambda p:p.y)
	da_df['centroid_lon'] = da_df[da_geometry].centroid.apply(lambda p:p.x)

	dadb_df = pd.merge(df, da_df[[DAUID, 'centroid_lat', 'centroid_lon']], on = DAUID)

	dadb_df['da_lon_w'] = np.where(dadb_df['da_lon_w'].isnull(), dadb_df['centroid_lon'], dadb_df['da_lon_w'])
	dadb_df['da_lat_w'] = np.where(dadb_df['da_lat_w'].isnull(), dadb_df['centroid_lat'], dadb_df['da_lat_w'])

	dadb_df.drop(labels = ['centroid_lat', 'centroid_lon'], axis = 1)

	return dadb_df

def map_weighted_centroid(df, region_id, local_centroid, weighted_centroid, weights, prop_maps, filename_prefix):
    '''
    Function to map regional weighted centroid against local geographic centriods. Visual indication
    of the sucess of the population wieghted centroids
    Inputs: df- dataframe containing all pertinent information
            region_id- column name of the ID of the larger region, will be used as base for map
            local_centroid- column name of centroid of the smaller, local region which will be plot against the regional, weighted centroid
            weighted_centroid- columns name of the population weighted centroid, calculated by calculate_weighted_centroid function
            weights- column name of the variable to be used as weights, most often population. Must be numeric type variable.
            prop_maps- number betweeon 0-1 indicating the proportion of region_ids to sample when creating maps. If maps of all
            regions is wanted, input 1
            filename_prefix- prefix to use when generating individual files of generated maps.
    Returns: nothing, but outputs pictures of the generated maps
    '''

    # getting random subset of regions
    all_IDs = list(set(list(df[region_id])))
    sample_IDs = sample(all_IDs, round(prop_maps * len(all_IDs)))

    for ID in sample_IDs:
        filename = '{}_{}.png'.format(filename_prefix, ID)

        subset = df[df[region_id] == ID]

        # creating map base of region outline
        base = subset.plot(color = 'white', edgecolor = 'black')

        # creating second layer of local geometric centroids
        subset_centroid = subset.set_geometry(local_centroid)
        base2 = subset_centroid.plot(ax=base, marker = 'o', color = 'red')

        # adding text to the map of local populations
        pops = []
        for x, y, label in zip(subset_centroid.geometry.x, subset_centroid.geometry.y, subset_centroid[weights]):
            pops.append(plt.text(x, y, label, fontsize = 8))

        # 3rd layer of population weighted centroid
        subset_CT_centroid = subset_centroid.set_geometry(weighted_centroid)
        subset_CT_centroid.plot(ax = base2, marker = 'o', color = 'blue').get_figure().savefig(filename)

def write_file(df, filename):
	'''
	Write dataframe to csv file
	Inputs: df- dataframe
			filename- filename to use when writing file
	Returns: nothing
	'''
	df.to_csv(filename, index = False)
