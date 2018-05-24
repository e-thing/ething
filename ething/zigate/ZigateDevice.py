# coding: utf-8


from ething.Device import Device, method, interface, attr, abstract, isString, isNone, isEnum


@abstract
@attr('address', validator=isString(allow_empty=False), description="The short address of this device on the zigbee network")
@attr('model', validator=isString(allow_empty=False) | isNone(), description="The model of this device")
@attr('manufacturer', validator=isString(allow_empty=False) | isNone(), description="The manufacturer of this device")
class ZigateDevice(Device):
    """
    ZigateDevice Device base class representation
    """

    @property
    def gateway(self):
        return self.createdBy

    def onMessage(self, message):
        pass

    def sendMessage(self, type, payload='', waitResponse=False):
        return self.gateway().sendMessage(type, payload, waitResponse)

    @method.return_type('application/json')
    def listEndPoints(self):
        """
        list available endpoints
        """
        return self.sendMessage('0045', self.address.rjust(4, '0'), True)

    @method.arg('endpoint', type='string', minLength=1, maxLength=2, description="hexadecimal format")
    @method.return_type('application/json')
    def getDescriptor(self, endpoint):
        """
        retrieve the descriptor of a given endpoint
        """
        return self.sendMessage('0043', self.address.rjust(4, '0')+endpoint.rjust(2, '0'), True)
