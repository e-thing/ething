

"""
 @swagger-definition
 "MySensorsEthernetGateway":{ 
   "type": "object",
   "description": "MySensorsEthernetGateway Device resource representation",
	 "allOf": [
		{
		   "$ref":"#/definitions/MySensorsGateway"
		},
		{  
		   "type": "object",
		   "properties":{
			 "address": {
				  "type":"string",
				  "description":"The ip address or hostname of the gateway."
			   }
		   }
		}
   ]
 }
"""
	 

from MySensorsGateway import MySensorsGateway
from ething.base import attr, isString

@attr('address', validator = isString(regex = '^([-\\w.]+)(:[0-9]{1,5})?$'))
class MySensorsEthernetGateway(MySensorsGateway):
	pass



if __name__ == "__main__":
	
	from ething.core import Core
	from random import randint
	import time
	
	core = Core({
		'db':{
			'database': 'test'
		},
		'log':{
			'level': 'debug'
		}
	})
	
	device = None
	
	devices = core.find({
		'type': 'MySensorsEthernetGateway'
	})
	
	if len(devices) > 1:
	
		for d in devices:
			print 'remove previous device...', d
			d.remove()
	
	elif len(devices) == 1:
		device = devices[0]
	
	if not device:
		device = core.create('MySensorsEthernetGateway', {
			'name': 'mysensors_gateway',
			'address': '192.168.1.117:5003'
		})
	
	
	print device
	
	print device.data
	
	print device.getVersion()
	

