import pandas as pd 
import numpy as np 

from Config import Config
from DataFrame import DataFrame

class CSVDataFrame(DataFrame):

	def __init__(self, filename, filetype, columns, required_columns, encoding = 'latin-1'):
		self.encoding = encoding 
		super().__init__(filename, filetype, columns, required_columns)

	def read_file(self):
		""" Read in csv file """
		df = pd.read_csv(self.name, encoding = self.encoding)

		return df
