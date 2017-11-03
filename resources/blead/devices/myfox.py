from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals

class Myfox():
	def __init__(self):
		self.name = 'myfox'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf=''):
		if name.lower() == self.name:
			return True
		if name.lower().find("myfox") != -1:
			return True
			
	def parse(self,data,mac,name):
		action={}
		action['present'] = 1
		return action

globals.COMPATIBILITY.append(Myfox)