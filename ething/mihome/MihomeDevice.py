

"""
 @swagger-definition
 "Device\\MihomeDevice":{ 
   "type": "object",
   "description": "Mihome Device base class.",
	 "allOf": [
		{
		   "$ref":"#/definitions/Device"
		},
		{  
		   "type": "object",
		   "properties":{
			 "sid": {
				  "type":"string",
				  "description":"The uniq sid of the device",
				  "readOnly": true
			   }
		   }
		}
   ]
 }
"""


from ething.Device import Device, method, attr, isString
import json

@attr('sid', validator = isString(allow_empty = False))
class MihomeDevice(Device):
	
	@property
	def gateway (self):
		return self.createdBy
	
	
	def processAttr(self, name, value):
		pass # to be implemented
	
	
	def processData (self, response):
		
		data = json.loads(response['data'])
		
		if isinstance(data, dict):
			
			for k in data:
				
				value = data[k]
				
				if k == 'voltage':
					self.store('voltage', int(value)/1000.) # volt
				else:
					self.processAttr(k, value)
	
	
	
	def sendCommand (self, cmd):
		return self.gateway.sendCommand(cmd)
	
	




