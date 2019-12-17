import requests
import pdb
import pandas as pd 
import numpy as np 
import math 
import time
import geopandas as gpd 
import re
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt

def get_supply_catchment(client, locations, catch_range, range_type, location_ids = None, sleep_time = 0):
    '''
    Calls ORS API and creates geodataframe of polygons indicating catchment area 
    Inputs: client- ORS client connection 
            locations- list of lat/lon points indicating supply locations 
            catch_range- range of catchment 
            range_type- range given in time or distance
            location_ids- IDs for each location, if None, sequential numbers will be applied as IDs
            sleep_time- time, in seconds, to rest between API calls. Defaults to 0 
    Returns: 
    '''
    polygons = []
    ids = []
    locations_list = []
    
    if location_ids == None: 
        location_ids = list(np.arange(len(locations)))
    
    for i, loc in zip(location_ids, locations):
        time.sleep(sleep_time)
        
        # body = {"locations": [loc], 
        #        "range": [catch_range]}

        # call = requests.post('https://api.openrouteservice.org/v2/isochrones/driving-car', json=body, headers=API_headers)

        call = client.isochrones(locations = [loc], 
						 profile = 'driving-car', 
						 range = [catch_range],
						 range_type = range_type,
						 units = 'm'
						 )

        # getting data for the isochrone polygon 

        iso_geometry = call['features'][0]['geometry']
        coords = np.array(iso_geometry['coordinates'][0])

        # converting isochrone coordinates from array to polygon, appending to master list 
        polygon_geom = Polygon(coords)
        
        polygons.append(polygon_geom)
        ids.append(i)
        locations_list.append(loc)
        
        
    crs = {'init':'epsg:4326'}
    
    # creating geodf from polygons
    polygon = gpd.GeoDataFrame(index = ids, crs = crs, geometry = polygons)
    polygon['id'] = ids
    polygon['location'] = locations_list

    return polygon

def filter_centroids(centroid_df, lat_col_name, lon_col_name, iso):
	'''
	Determines whether centroids are contained within specific service canada catchments
	Inputs: centroid_df- table with centroid data 
			lat_col_name- column name with latitude data
			lon_col_name- column name with longitude data 
			iso- individual service canada catchment 
	Returns: centroids within catchment 
	'''
	geometry = [Point(xy) for xy in zip(centroid_df[lon_col_name], centroid_df[lat_col_name])]
	crs = {'init': 'epsg:4326'}

	centroids_gdf = gpd.GeoDataFrame(centroid_df, crs=crs, geometry=geometry)

	centroids_gdf['in_iso'] = centroids_gdf['geometry'].map(lambda x: True if iso.geometry.contains(x) == True else False)

	return centroids_gdf['in_iso']

def dist_m_wrapper(client, POS_IDs, centroid_df, iso_df, dm_metric, dm_unit, centroid_ID_col, centroid_lat_col, centroid_lon_col, sleep_time = 0): 
	'''
	Wrapper function for getting distance matrix- goes through service canada centres, filters centroids, calls get_dist_m, saves result in original df 
	Inputs: client- client connection for ORS 
			POS_IDs- list of service canada center IDs
			iso_df- table with polygons of catchments
			dm_metric- what metric to use when calculating distance matrix (distance, duration)
			dm_unit- unit of measurement to use in distance matrix 
			centroid_ID_col- column name of centroid ID 
			centroid_lat_col- column name of latitude data
			centroid_lon_col- column name of longitude data 
			sleep_time-  time, in seconds, to rest between API calls. Defaults to 0 
	Returns: centroid_df with distance matrix data in there !
	'''

	for posID in POS_IDs:

		colname = 'POS_' + str(posID)
		pos = iso_df[iso_df['id'] == posID]['location'].tolist()
		centroid_subset = centroid_df[centroid_df[colname]]
		dm_name = 'POS' + str(posID) + '_' + dm_metric
		if len(centroid_subset.index) > 0:
			result = get_dist_m(client, centroid_subset, pos, centroid_lat_col, centroid_lon_col, dm_metric, dm_unit)
		else:
			centroid_subset[dm_name] = np.nan
			result = centroid_subset
		result.rename(columns = {dm_metric: dm_name}, inplace = True)
		centroid_df = centroid_df.merge(result[[centroid_ID_col, dm_name]], how = 'left', on = centroid_ID_col)
		centroid_df.drop(labels = colname, axis = 1, inplace = True)
	
	return centroid_df

def get_dist_m(client, df, pos, lat_col_name, lon_col_name, distance_metric, distance_unit, sleep_time = 0):
	'''
	Function to call ORS API and retrieve distance information for individual service canada centers 
	Inputs: client- ORS client 
			df- centroid table 
			pos- service canada center latitue/longitude 
			lat_col_name- name of column latitude
			lon_col_name- name of column longitude 
			distance_metric- metric to use for distance matrix call 
			distance_unit- unit of measurement for distance matrix call 
			sleep_time- time to rest between API calls, defaults to 0 
	Returns: distance matrix table for one service canada center 
	'''
	# breaking df into smaller chunks 
	num_groups = math.ceil(len(df) / 1000)
	all_result = []

	for min_df in np.array_split(df, num_groups): 

		centroid_list = min_df[[lon_col_name, lat_col_name]].values.tolist()

		locations = pos + centroid_list

		call = client.distance_matrix(locations = locations, 
			destinations = [0], 
			profile = 'driving-car',
			metrics = [distance_metric],
			units = distance_unit)

		result = call[distance_metric + 's']

		result.pop(0)

		# flattening list of lists
		result = sum(result, [])

		all_result.append(result)


	all_result = sum(all_result, [])

	df[distance_metric] = all_result

	return df
    


