import json

# when running app
try:
	with open('../config.json') as json_data_file:
		config = json.load(json_data_file)

# when running InitSchema
except:
	with open('config.json') as json_data_file:
		config = json.load(json_data_file)

JSON_ERROR = 'JSON Error. Unable to read config for file '

class Data():

	def __init__(self):
	
		# files
		try:
			self.demand_geo_weight_file = config['files']['demand_geo_weight']['file']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo_weight')

		try:
			self.demand_geo_file = config['files']['demand_geo']['file']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo')

		try:
			self.demand_pop_file = config['files']['demand_pop']['file']
		except(KeyError):
			print(JSON_ERROR + 'demand_pop')

		try:
			self.supply_file = config['files']['supply']['file']
		except(KeyError):
			print(JSON_ERROR + 'supply')

		try:
			self.supply_crs = config['files']['supply']['crs']
		except(KeyError):
			print(JSON_ERROR + 'supply')

		# file types
		try:
			self.demand_geo_weight_type = config['files']['demand_geo_weight']['type']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo_weight')

		try:
			self.demand_geo_type = config['files']['demand_geo']['type']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo')

		try:
			self.demand_pop_type = config['files']['demand_pop']['type']
		except(KeyError):
			print(JSON_ERROR + 'demand_pop')

		try:
			self.supply_type = config['files']['supply']['type']
		except(KeyError):
			print(JSON_ERROR + 'supply')


		# encoding

		try:
			self.demand_pop_encode = config['files']['demand_pop']['encoding']
		except(KeyError):
			print(JSON_ERROR + 'demand_pop')

		try:
			self.lrgpop_encode = None
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.supply_encode = config['files']['supply']['encoding']
		except(KeyError):
			print(JSON_ERROR + 'supply')

		# projection
		try:
			self.demand_geo_weight_crs = config['files']['demand_geo_weight']['crs']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo_weight')

		try:
			self.demand_geo_crs = config['files']['demand_geo']['crs']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo')

		# columns
		try:
			self.demand_geo_weight_columns = config['files']['demand_geo_weight']['columns']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo_weight')

		try:
			self.demand_geo_columns = config['files']['demand_geo']['columns']
		except(KeyError):
			print(JSON_ERROR + 'demand_geo')

		try:
			self.demand_pop_columns = config['files']['demand_pop']['columns']
		except(KeyError):
			print(JSON_ERROR + 'demand_pop')

		try:
			self.supply_columns = config['files']['supply']['columns']
		except(KeyError):
			print(JSON_ERROR + 'supply')

		## ORS stuff

		try:
			self.ORS_client = config['ORS']['connection']['client_url']
			self.ORS_timeout = config['ORS']['connection']['timeout']

			self.iso_catchment_range = config['ORS']['isochrones']['catchment_range']
			self.iso_catchment_type = config['ORS']['isochrones']['catchment_range_type']
			self.iso_profile = config['ORS']['isochrones']['profile']
			self.iso_sleep_time = config['ORS']['isochrones']['sleep_time']

			self.dm_metric = config['ORS']['distance_matrix']['metric']
			self.dm_unit = config['ORS']['distance_matrix']['unit']
			self.dm_sleep_time = config['ORS']['distance_matrix']['sleep_time']
			
		except(KeyError):
			print(JSON_ERROR)


		self.required_cols = {}
		self.required_cols['shape'] = ['ID', 'LRG_ID', 'geometry']
		self.required_cols['demand'] = ['ID', 'demand_total']
		self.required_cols['supply'] = ['ID', 'latitude', 'longitude']

		self.types_dict = {'str': [str, 'O'], 'int': [float, int]}
	
class Database():	
	def __init__(self):

		self.NAME = config['DB']['NAME']
		self.HOST = config['DB']['HOST']
		self.PASSWORD = config['DB']['PASSWORD']
		self.USER = config['DB']['USER']

class Logger():
	def __init__(self):
		
		self.DEFAULT_LEVEL = config['LOGGER']['DEFAULT_LEVEL']
		self.FILE = config['LOGGER']['FILE']
		self.FILE_PATH = config['LOGGER']['FILE_PATH']

class App():
	def __init__(self):

		self.SECRET_KEY = config['APP']['SECRET_KEY']
		self.HOST = config['APP']['HOST']
		self.PORT = config['APP']['PORT']
		self.THREADS = config['APP']['THREADS']
		
