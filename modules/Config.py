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
			self.sml_popfile = None
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.lrg_popfile = None
		except(KeyError):
			print(JSON_ERROR)
				
		try:
			self.pos_file = None
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
			self.smlpop_type = None
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.lrgpop_type = None
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.pos_type = None 
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
			self.smlpop_columns = None
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.lrgpop_columns = None
		except(KeyError):
			print(JSON_ERROR)

		try:
			self.pos_columns = None 
		except(KeyError):
			print(JSON_ERROR)


		self.required_cols = {}
		self.required_cols['shape'] = ['ID', 'geometry']
		self.required_cols['weight'] = ['ID', 'weight']
		self.required_cols['POI'] = ['ID', 'latitude', 'longitude']