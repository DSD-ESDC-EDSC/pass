import pandas as pd 
import numpy as np 
import json

from Config import Config 
from DataFrame import DataFrame
from GeoDataFrame import GeoDataFrame
from CSVDataFrame import CSVDataFrame
from weighted_centroid import WeightedCentroid

if __name__ == '__main__':
	config = Config('config.json')

	large_shape = GeoDataFrame(config.lrg_shapefile, config.lrgshape_type, config.lrgshape_columns, config.required_cols[config.lrgshape_type], config.lrgshape_projection)  #filename, filetype, encoding, columns, required_columns
	small_shape = GeoDataFrame(config.sml_shapefile, config.smlshape_type, config.smlshape_columns, config.required_cols[config.smlshape_type], config.smlshape_projection)
	small_pop = CSVDataFrame(config.sml_popfile, config.smlpop_type, config.smlpop_columns, config.required_cols[config.smlpop_type], config.smlpop_encode)

	small_shape.merge_DataFrame(small_pop)

	centroid = WeightedCentroid(small_shape, large_shape)
	weighted_centroid_df = centroid.calculate_weighted_centroid()
	centroid.map_weighted_centroid(0.001, 'test_maps/test')

	import pdb; pdb.set_trace()
