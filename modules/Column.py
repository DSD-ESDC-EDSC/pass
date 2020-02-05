import pandas as pd 
import numpy as np 


class Column:

	def __init__(self, colname, coltype, coldesc, unit):

		self.colname = colname
		self.coltype = coltype
		self.coldesc = coldesc
		self.colunit = unit

	def get_colname(self):
		return self.colname

	def get_coltype(self):
		return self.coltype

	def get_coldesc(self):
		return self.coldesc

	def get_colunit(self):
		return self.colunit
