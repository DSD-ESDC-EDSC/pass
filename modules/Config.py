import json


JSON_ERROR = 'JSON Error. Unable to read config for file '

class Config:

	def __init__(self, config_file):
		self.config_file = config_file

		with open('config.json') as json_data_file:
			data = json.load(json_data_file)


		# files
		try:
			self.demand_geo_weight_file = data['files']['demand_geo_weight']['file']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo_weight')

		try:
			self.demand_geo_file = data['files']['demand_geo']['file']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo')

		try:
			self.demand_pop_file = data['files']['demand_pop']['file']
		except(KeyError):
			print(JSON_ERROR + 'demand_pop')

		try:
			self.supply_file = data['files']['supply']['file']
		except(KeyError):
			print(JSON_ERROR + 'supply')

		try:
			self.supply_crs = data['files']['supply']['crs']
		except(KeyError):
			print(JSON_ERROR + 'supply')

		# file types
		try:
			self.demand_geo_weight_type = data['files']['demand_geo_weight']['type']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo_weight')

		try:
			self.demand_geo_type = data['files']['demand_geo']['type']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo')

		try:
			self.demand_pop_type = data['files']['demand_pop']['type']
		except(KeyError):
			print(JSON_ERROR + 'demand_pop')

		try:
			self.supply_type = data['files']['supply']['type']
		except(KeyError):
			print(JSON_ERROR + 'supply')


		# encoding

		try:
			self.demand_pop_encode = data['files']['demand_pop']['encoding']
		except(KeyError):
			print(JSON_ERROR + 'demand_pop')

		try:
			self.lrgpop_encode = None
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.supply_encode = data['files']['supply']['encoding']
		except(KeyError):
			print(JSON_ERROR + 'supply')

		# projection
		try:
			self.demand_geo_weight_crs = data['files']['demand_geo_weight']['crs']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo_weight')

		try:
			self.demand_geo_crs = data['files']['demand_geo']['crs']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo')

		# columns
		try:
			self.demand_geo_weight_columns = data['files']['demand_geo_weight']['columns']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo_weight')

		try:
			self.demand_geo_columns = data['files']['demand_geo']['columns']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo')

		try:
			self.demand_pop_columns = data['files']['demand_pop']['columns']
		except(KeyError):
			print(JSON_ERROR + 'demand_pop')

		try:
			self.supply_columns = data['files']['supply']['columns']
		except(KeyError):
			print(JSON_ERROR + 'supply')

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
		self.required_cols['demand'] = ['ID', 'demand']
		self.required_cols['supply'] = ['ID', 'LRG_ID', 'latitude', 'longitude']

		self.types_dict = {'str': [str, 'O'], 'int': [float, int]}
