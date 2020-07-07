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

# configuration class for reading in data for database
class Data():

	def __init__(self):
		self.config = config
		# files
		try:
			self.demand_geo_weight_file = config['FILES']['DEMAND_GEO_WEIGHT']['FILE']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_GEO_WEIGHT')

		try:
			self.demand_geo_file = config['FILES']['DEMAND_GEO']['FILE']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_GEO')

		try:
			self.demand_pop_file = config['FILES']['DEMAND_POP']['FILE']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_POP')

		try:
			self.poi_file = config['FILES']['POI']['FILE']
		except(KeyError):
			print(JSON_ERROR + 'POI')

		try:
			self.poi_crs = config['FILES']['POI']['CRS']
		except(KeyError):
			print(JSON_ERROR + 'POI')

		# file types
		try:
			self.demand_geo_weight_type = config['FILES']['DEMAND_GEO_WEIGHT']['TYPE']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_GEO_WEIGHT')

		try:
			self.demand_geo_type = config['FILES']['DEMAND_GEO']['TYPE']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_GEO')

		try:
			self.demand_pop_type = config['FILES']['DEMAND_POP']['TYPE']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_POP')

		try:
			self.poi_type = config['FILES']['POI']['TYPE']
		except(KeyError):
			print(JSON_ERROR + 'POI')


		# encoding

		try:
			self.demand_pop_encode = config['FILES']['DEMAND_POP']['ENCODING']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_POP')

		try:
			self.lrgpop_encode = None
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.poi_encode = config['FILES']['POI']['ENCODING']
		except(KeyError):
			print(JSON_ERROR + 'POI')

		# projection
		try:
			self.demand_geo_weight_crs = config['FILES']['DEMAND_GEO_WEIGHT']['CRS']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_GEO_WEIGHT')

		try:
			self.demand_geo_crs = config['FILES']['DEMAND_GEO']['CRS']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_GEO')

		# columns
		try:
			self.demand_geo_weight_columns = config['FILES']['DEMAND_GEO_WEIGHT']['COLUMNS']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_GEO_WEIGHT')

		try:
			self.demand_geo_columns = config['FILES']['DEMAND_GEO']['COLUMNS']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_GEO')

		try:
			self.demand_pop_columns = config['FILES']['DEMAND_POP']['COLUMNS']
		except(KeyError):
			print(JSON_ERROR + 'DEMAND_POP')

		try:
			self.poi_columns = config['FILES']['POI']['COLUMNS']
		except(KeyError):
			print(JSON_ERROR + 'POI')

		## ORS connection information

		try:
			self.ORS_client = config['ORS']['CONNECTION']['CLIENT_URL']
			self.ORS_timeout = config['ORS']['CONNECTION']['TIMEOUT']

			self.iso_catchment_range = config['ORS']['ISOCHRONES']['CATCHMENT_RANGE']
			self.iso_catchment_type = config['ORS']['ISOCHRONES']['CATCHMENT_RANGE_TYPE']
			self.iso_profile = config['ORS']['ISOCHRONES']['PROFILE']
			self.iso_sleep_time = config['ORS']['ISOCHRONES']['SLEEP_TIME']

			self.dm_metric = config['ORS']['DISTANCE_MATRIX']['METRIC']
			self.dm_unit = config['ORS']['DISTANCE_MATRIX']['UNIT']
			self.dm_sleep_time = config['ORS']['DISTANCE_MATRIX']['SLEEP_TIME']
			
		except(KeyError):
			print(JSON_ERROR)


		self.required_cols = {}
		self.required_cols['shape'] = ['ID', 'LRG_ID', 'GEOMETRY']
		self.required_cols['demand'] = ['ID', 'DEMAND_TOTAL']
		self.required_cols['poi'] = ['ID', 'LATITUDE', 'LONGITUDE']

		self.types_dict = {'str': [str, 'O'], 'int': [float, int]}

# configuration class for database connection
class Database():	
	def __init__(self):

		self.NAME = config['DB']['NAME']
		self.HOST = config['DB']['HOST']
		self.PASSWORD = config['DB']['PASSWORD']
		self.USER = config['DB']['USER']

# configuration class for logger
class Logger():
	def __init__(self):
		
		self.DEFAULT_LEVEL = config['LOGGER']['DEFAULT_LEVEL']
		self.FILE = config['LOGGER']['FILE']
		self.FILE_PATH = config['LOGGER']['FILE_PATH']

# configuration class for app
class App():
	def __init__(self):

		self.SECRET_KEY = config['APP']['SECRET_KEY']
		self.HOST = config['APP']['HOST']
		self.PORT = config['APP']['PORT']
		self.THREADS = config['APP']['THREADS']

# configuration class for map
class Basemap():
	def __init__(self):

		self.TOKEN = config['BASEMAP']['TOKEN']
