from weighted_centroid import * 
from distance_matrix import * 
import sys
import pdb 
import openrouteservice as ors
import json

with open("../config.json") as f:
    config = json.load(f)

# setting up the variables! 

client_url = "http://10.54.61.201:8080/ors"
timeout = 500
CMAUID_tofilter = 462

# weighted centroid
census_shapefile = config['census_shapefile']
census_popfile = config['census_popfile']
census_shapefile_DA = config['census_shapefile_DA']
cpop_colstokeep = ['DBuid/IDidu', ' DBpop2016/IDpop2016']
cpop_colnames = ['DBUID', 'DB_Population']
DBUID = 'DBUID'
DAUID = 'DAUID'
DA_geometry = 'geometry'
DB_geometry = 'geometry'
DB_population = 'DB_Population'
centroid_filename = 'weighted_centroid.csv'

# distance matrix 
POS_file = config['POS_file']

POS_colstokeep = None 
POS_colnames = None 
POS_lon_col = 'Longitude'
POS_lat_col = 'Latitude'
POS_ID = 'OBJECTID'
web_projection = 'epsg:4326'
statcan_projection = 'epsg:3347'

centroid_colstokeep = ['DAUID', 'CMAUID', 'PRNAME', 'CSDNAME', 'da_population']

isochrone_range = 1800
isochrone_range_type = 'time'
isochrone_sleep_time = 0

dm_metric = 'distance'
dm_unit = 'm'
dm_sleep_time = 0

dm_filename = 'distance_matrix_30min.csv'


client = ors.Client(key="", base_url = client_url, timeout = timeout, retry_over_query_limit = True)

################################
###### GET CENTROID  DATA ######
################################
'''
# reading in files 
shape_df = read_files(census_shapefile, 'shape')
pop_df = read_files(census_popfile, 'csv', 'ISO-8859-1')

# preprocessing 
pop_df = subset_df(pop_df, cpop_colstokeep)
pop_df = rename_cols(pop_df, cpop_colnames)

pop_df[DBUID] = pop_df[DBUID].astype(str)

# merging to 1 
df = shape_df.merge(pop_df, on = DBUID)

centroids = calculate_weighted_centroid(df, DAUID, DA_geometry, DB_population)

centroids = centroids.groupby(DAUID).first().reset_index()

centroids_nonull = impute_missing_centroid(centroids, read_files(census_shapefile_DA, 'shape'), DAUID, DA_geometry)

centroids_nonull = centroids_nonull[['DAUID', 'DBUID', 'DBRPLAMX', 'DBRPLAMY', 'PRUID', 'PRNAME', 'CDUID', 'CDNAME',
'CDTYPE', 'CCSUID', 'CCSNAME', 'CSDUID', 'CSDNAME', 'CSDTYPE', 'ERUID', 'ERNAME', 'FEDUID', 'FEDNAME',
'SACCODE', 'SACTYPE', 'CMAUID', 'CMAPUID', 'CMANAME', 'CMATYPE', 'CTUID', 'CTNAME', 'ADAUID',
'DB_Population', 'db_lon', 'db_lat', 'da_lon_w', 'da_lat_w', 'da_population']]

write_file(centroids_nonull, centroid_filename)
'''
#################################
###### GET DISTANCE MATRIX ######
#################################

#### Creating isochrones 

# read in file 
pos = read_files(POS_file, 'csv', 'ISO-8859-1')

# filtering df 
pos_subset = pos[pos['CMAUID'] == str(CMAUID_tofilter)]

pos_subset['POS_point'] = [Point(xy) for xy in zip(pos_subset.Longitude, pos_subset.Latitude)]

pos_gdf = gpd.GeoDataFrame(pos_subset, geometry = pos_subset['POS_point'], crs = {'init': web_projection})

locations = pos_gdf[['Longitude', 'Latitude']].values.tolist()
ids = pos_gdf['OBJECTID'].tolist()

iso = get_supply_catchment(client, locations, isochrone_range, isochrone_range_type, ids, isochrone_sleep_time)

if type(iso) == tuple: 
	print('ORS error')
	print(iso)
	sys.exit(0)

#### Sorting centroids 

cent = read_files(centroid_filename, 'csv')
cent_subset = cent[cent['CMAUID'] == CMAUID_tofilter]

cent_gdf = gpd.GeoDataFrame(cent_subset, geometry = [Point(xy) for xy in zip(cent_subset.da_lon_w, cent_subset.da_lat_w)], crs = {'init': statcan_projection})

cent_gdf = cent_gdf.to_crs({'init': web_projection})   # need to change projection to 4326 to work with ORS 
cent_gdf['proj_lat'] = cent_gdf['geometry'].y
cent_gdf['proj_lon'] = cent_gdf['geometry'].x

centroid_colstokeep = centroid_colstokeep + ['proj_lat', 'proj_lon']

cent_gdf_subset = subset_df(cent_gdf, centroid_colstokeep)

for index, row in iso.iterrows(): 
    cent_gdf_subset['POS_' + str(row['id'])] = filter_centroids(cent_gdf_subset, 'proj_lat', 'proj_lon', row)

cent_gdf_nonull = cent_gdf_subset[(cent_gdf_subset['proj_lat'].isnull() == False) & (cent_gdf_subset['proj_lon'].isnull() == False)]

#### Getting distance matrix

catchment_list = iso['id'].tolist()

centroids_w_distance = dist_m_wrapper(client, catchment_list, cent_gdf_nonull, iso, dm_metric, dm_unit, DAUID, 'proj_lat', 'proj_lon')

write_file(centroids_w_distance, dm_filename)

