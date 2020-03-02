import json


JSON_ERROR = 'JSON Error. Please ensure format is correct.'

class Config:

	def __init__(self, config_file):
		self.config_file = config_file 

		with open('config.json') as json_data_file: 
			data = json.load(json_data_file)


		# files 
		try: 
			self.sml_shapefile = data['files']['shape_small']['file']
		except(KeyError):
			print(JSON_ERROR)

		try:	
			self.lrg_shapefile = data['files']['shape_large']['file']
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.sml_popfile = data['files']['population_small']['file']
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.lrg_popfile = None
		except(KeyError):
			print(JSON_ERROR)
				
		try:
			self.supply_file = data['files']['supply']['file']
		except(KeyError):
			print(JSON_ERROR)

		# file types 
		try:
			self.smlshape_type = data['files']['shape_small']['type']
		except(KeyError):
			print(JSON_ERROR)

		try:	
			self.lrgshape_type = data['files']['shape_large']['type']
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.smlpop_type = data['files']['population_small']['type']
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.lrgpop_type = None
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.supply_type = data['files']['supply']['type'] 
		except(KeyError):
			print(JSON_ERROR)


		# encoding

		try:
			self.smlpop_encode = data['files']['population_small']['encoding']
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.lrgpop_encode = None
		except(KeyError):
			print(JSON_ERROR)
				
		try:
			self.supply_encode = data['files']['supply']['encoding']
		except(KeyError):
			print(JSON_ERROR)

		# projection 
		try:
			self.smlshape_projection = data['files']['shape_small']['projection']
		except(KeyError):
			print(JSON_ERROR)

		try:	
			self.lrgshape_projection = data['files']['shape_large']['projection']
		except(KeyError):
			print(JSON_ERROR)

		# columns 
		try:
			self.smlshape_columns = data['files']['shape_small']['columns']
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.lrgshape_columns = data['files']['shape_large']['columns']
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.smlpop_columns = data['files']['population_small']['columns']
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.lrgpop_columns = None
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.supply_columns = data['files']['supply']['columns']
		except(KeyError):
			print(JSON_ERROR)

		## ORS stuff 

		try: 
			self.ORS_client = data['ORS_params']['connection']['client_url']
			self.ORS_timeout = data['ORS_params']['connection']['timeout']

			self.iso_catchment_range = data['ORS_params']['isochrones']['catchment_range']
			self.iso_catchment_type = data['ORS_params']['isochrones']['catchment_range_type']
			self.iso_profile = data['ORS_params']['isochrones']['profile']
			self.iso_sleep_time = data['ORS_params']['isochrones']['sleep_time']

			self.dm_metric = data['ORS_params']['distance_matrix']['metric']
			self.dm_unit = data['ORS_params']['distance_matrix']['unit']
			self.dm_sleep_time = data['ORS_params']['distance_matrix']['sleep_time']
		except(KeyError):
			print(JSON_ERROR)


		self.required_cols = {}
		self.required_cols['shape'] = ['ID', 'LRG_ID', 'geometry']
		self.required_cols['demand'] = ['ID']
		self.required_cols['supply'] = ['ID', 'LRG_ID', 'latitude', 'longitude']

		self.types_dict = {'str': [str, 'O'], 'int': [float, int]}