


"""
 @swagger-definition
 "RFLinkGateway":{ 
   "type": "object",
   "description": "RFLinkGateway Device resource representation",
	 "allOf": [
		{
		   "$ref":"#/definitions/Device"
		},
		{  
		   "type": "object",
		   "properties":{
			 "version": {
				  "type":"string",
				  "description":"The version of the RFLink library used.",
				  "readOnly": true
			   },
			 "revision": {
				  "type":"string",
				  "description":"The revision number of the RFLink library used.",
				  "readOnly": true
			   },
			 "build": {
				  "type":"string",
				  "description":"The build number of the RFLink library used.",
				  "readOnly": true
			   }
		   }
		}
   ]
 }
"""


from ething.Device import Device, method, attr, isString, isBool, isNone, READ_ONLY




@attr('version', default=None, mode = READ_ONLY)
@attr('revision', default=None, mode = READ_ONLY)
@attr('build', default=None, mode = READ_ONLY)
class RFLinkGateway(Device):
	
	
	def getNodes (self, filter = None):
		q = {
			'type' : 'RFLinkNode',
			'createdBy' : self.id
		}
		
		if filter is not None:
			q = {
				'and' : [q, filter]
			}
		
		return self.ething.find(q)
	
	
	def getNode (self, filter):
		return self.ething.findOne({
			'and' : [
				{
					'type' : 'RFLinkNode',
					'createdBy' : self.id
				}, filter
			]
		})
	
	
	def removeAllNodes (self):
		# remove all the nodes attached to it !
		for node in self.getNodes():
			node.remove()
	
	
	
	def remove (self, removeChildren = False):
		
		# remove all the nodes attached to it !
		self.removeAllNodes()
		
		# remove the resource
		super(RFLinkGateway, self).remove(removeChildren)
		
	
	
	@method.arg('message', type='string', minLength = 1)
	@method.return_type('text/plain')
	def sendMessage (self, message):
		"""
		send a message.
		"""
		return self.ething.rpc.request('device.rflink.send', self.id, message)
	
	
	# send a message and wait for the response.
	# note: not all request has a response !
	def sendMessageWaitResponse (self, message):
		return self.ething.rpc.request('device.rflink.sendWaitResponse', self.id, message)
	
	
	def reboot(self):
		"""
		reboot the gateway.
		"""
		device.sendMessage("10;REBOOT;")
	
	@method.return_type('text/plain')
	def getVersion (self):
		"""
		get the version of the gateway.
		"""
		error, _, resp = self.sendMessageWaitResponse("10;VERSION;")
		if error:
			raise Exception(error)
		return resp.split(';', 2)[-1]
	
	def startInclusion(self):
		"""
		Put this gateway into inclusion mode. Unknown devices will be added automatically.
		"""
		device.setData("inclusion", True)
	
	def stopInclusion(self):
		"""
		Quit the inclusion mode for this gateway.
		"""
		device.setData("inclusion", False)
	
	
	
	




