

"""
 @swagger-definition
 "MySensorsGateway":{ 
   "type": "object",
   "description": "MySensorsGateway Device resource representation",
	 "allOf": [
		{
		   "$ref":"#/definitions/Device"
		},
		{  
		   "type": "object",
		   "properties":{
			 "isMetric": {
				  "type":"boolean",
				  "description":"Set the unit to Metric(default) instead of Imperial."
			   },
			 "libVersion": {
				  "type":"string",
				  "description":"The version of the MySensors library used.",
				  "readOnly": true
			   }
		   }
		}
   ]
 }
"""

from ething.Device import Device, method, attr, isString, isBool, isNone, READ_ONLY
from ething.Helpers import dict_recursive_update
import MySensors
from Message import Message


@attr('isMetric', validator = isBool(), default=True)
@attr('libVersion', default=None, mode = READ_ONLY)
class MySensorsGateway(Device):
	
	
	def getNodes (self, filter = None):
		q = {
			'type' : 'MySensorsNode',
			'createdBy' : self.id
		}
		
		if filter is not None:
			q = {
				'and' : [q, filter]
			}
		
		return self.ething.find(q)
	
	
	def getNode (self, nodeId):
		return self.ething.findOne({
			'type' : 'MySensorsNode',
			'createdBy' : self.id,
			'nodeId' : nodeId
		})
	
	
	def removeAllNodes (self):
		# remove all the nodes attached to it !
		for node in self.getNodes():
			node.remove()
	
	
	def remove (self, removeChildren = False):
		
		# remove all the nodes attached to it !
		self.removeAllNodes()
		
		# remove the resource
		super(MySensorsGateway, self).remove(removeChildren)
		
	
	
	@method.arg('nodeId', type='integer', minimum=0, maximum=255, required = True)
	@method.arg('sensorId', type='integer', minimum=0, maximum=255, required = True)
	@method.arg('type', type='integer', minimum=0, maximum=4, required = True)
	@method.arg('ack', type='bool', default = False)
	@method.arg('subtype', type='integer', minimum=0, maximum=255, required = True)
	@method.arg('payload', type='string', default = "", maxLength=25)
	@method.return_type('application/json')
	def sendMessage (self, nodeId, sensorId = None, type = None, ack = None, subtype = None, payload = None):
		"""
		send a message.
		"""
		
		message = None
		
		if isinstance(nodeId, Message):
			message = nodeId
		else:
			message = Message(nodeId,sensorId,type,ack,subtype,payload)
		
		return self.ething.rpc.request('device.mysensors.send', self.id, message)
	
	
	# send a message and wait for the response.
	# note: not all request has a response !
	def sendMessageWaitResponse (self, message):
		return self.ething.rpc.request('device.mysensors.sendWaitResponse', self.id, message)
	
	
	@method.return_type('string')
	def getVersion(self):
		"""
		request gateway version.
		"""
		error, _, resp = self.sendMessageWaitResponse(Message(MySensors.GATEWAY_ADDRESS, MySensors.INTERNAL_CHILD, MySensors.INTERNAL, MySensors.NO_ACK, MySensors.I_VERSION))
		if error:
			raise Exception(error)
		return resp.payload
	
	
	@method
	def reboot(self):
		"""
		Request gateway to reboot.
		"""
		self.sendMessage(Message(MySensors.GATEWAY_ADDRESS, MySensors.INTERNAL_CHILD, MySensors.INTERNAL, MySensors.NO_ACK, MySensors.I_REBOOT))




