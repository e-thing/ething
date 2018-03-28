

"""
 @swagger-definition
 "Device\\ZigateDevice":{ 
   "type": "object",
   "description": "ZigateDevice Device base class representation",
	 "allOf": [
		{
		   "$ref":"#/definitions/Device"
		},
		{  
		   "type": "object",
		   "properties":{
			 "address": {
				  "type":"string",
				  "description":"The short address of this device on the zigbee network"
			   }
		   }
		}
   ]
 }
"""


from ething.Device import Device, method, interface, attr, isString, isNone, isEnum



@attr('address', validator = isString(allow_empty=False))
@attr('model', validator = isString(allow_empty=False) | isNone())
@attr('manufacturer', validator = isString(allow_empty=False) | isNone())
class ZigateDevice(Device):
	
	
	
	@property
	def gateway (self):
		return self.createdBy
	
	
	
	def onMessage (self, message):
		pass
	
	
	
	def sendMessage (self, type, payload = '', waitResponse = False):
		return self.gateway().sendMessage(type, payload, waitResponse)
	
	
	@method.return_type('application/json')
	def listEndPoints(self):
		"""
		list available endpoints
		"""
		return self.sendMessage('0045', self.address.rjust(4, '0'), True)
	
	
	@method.arg('endpoint', type = 'string', minLength=1, maxLength=2, description="hexadecimal format")
	@method.return_type('application/json')
	def getDescriptor(self, endpoint):
		"""
		retrieve the descriptor of a given endpoint
		"""
		return self.sendMessage('0043', self.address.rjust(4, '0')+endpoint.rjust(2, '0'), True)




