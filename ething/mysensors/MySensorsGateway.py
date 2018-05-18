# coding: utf-8


from future.utils import string_types
from ething.Device import Device, method, attr, abstract, isString, isBool, isNone, READ_ONLY
from ething.Helpers import dict_recursive_update
from .helpers import *
from .Message import Message


@abstract
@attr('isMetric', validator = isBool(), default=True, description="Set the unit to Metric(default) instead of Imperial.")
@attr('libVersion', default=None, mode = READ_ONLY, description="The version of the MySensors library used.")
class MySensorsGateway(Device):
    """
    see https://www.mysensors.org
    """
    
    def getNodes (self, filter = None):
        q = {
            'type' : 'MySensorsNode',
            'createdBy' : self.id
        }
        
        if filter is not None:
            q = {
                '$and' : [q, filter]
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
        elif isinstance(nodeId, string_types):
            message = Message.parse(nodeId)
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
        error, _, resp = self.sendMessageWaitResponse(Message(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, NO_ACK, I_VERSION))
        if error:
            raise Exception(error)
        return resp.payload
    
    
    @method
    def reboot(self):
        """
        Request gateway to reboot.
        """
        self.sendMessage(Message(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, NO_ACK, I_REBOOT))




