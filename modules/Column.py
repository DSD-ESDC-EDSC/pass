import pandas as pd 
import numpy as np 


class Column:

	def __init__(self, colname, coltype, coldesc, unit):

		self.colname = colname
		self.coltype = coltype
		self.coldesc = coldesc
		self.colunit = unit

	def get_colname(self):
		""" Returns name of column """
		return self.colname

	def get_coltype(self):
		""" Returns type of column """
		return self.coltype

	def get_coldesc(self):
		""" Returns description of column """
		return self.coldesc

	def get_colunit(self):
		""" Return unit of column """
		return self.colunit
