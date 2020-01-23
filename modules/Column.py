import pandas as pd 
import numpy as np 


class Column:

	def __init__(self, colname, coltype, colunit):

		self.colname = colname
		self.coltype = coltype
		self.colunit = colunit

	def get_colname(self):
		return self.colname

	def get_coltype(self):
		return self.coltype

	def get_colunit(self):
		return self.colunit
