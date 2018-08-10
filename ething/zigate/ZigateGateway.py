# coding: utf-8


from ething.Device import Device, method, attr, abstract, isString, isBool, isNone, READ_ONLY
from .Message import Message


@abstract
@attr('appVersion', default=None, description="The version of the Zigate firmware.")
@attr('sdkVersion', default=None, description="The version of the Zigate SDK.")
class ZigateGateway(Device):

    def getDevices(self, filter=None):
        q = {
            'extends': 'resources/ZigateDevice',
            'createdBy': self.id
        }

        if filter is not None:
            q = {
                '$and': [q, filter]
            }

        return self.ething.find(q)

    def getDevice(self, addr):
        return self.ething.findOne({
            'extends': 'resources/ZigateDevice',
            'createdBy': self.id,
            'address': addr
        })

    def removeAllDevices(self):
        # remove all the nodes attached to it !
        for dev in self.getDevices():
            dev.remove()

    def remove(self, removeChildren=False):

        # remove all the nodes attached to it !
        self.removeAllDevices()

        # remove the resource
        super(ZigateGateway, self).remove(removeChildren)

    @method.arg('type', type='string', minLength=1)
    @method.return_type('text/plain')
    def sendMessage(self, type, payload='', waitResponse=False):
        """
        send a message.
        """
        return self.ething.rpc.request('device.zigate.send', self.id, Message(type, payload), waitResponse)

    @method.return_type('string')
    def getVersion(self):
        """
        request gateway version
        """
        err, response = self.sendMessage('0010', waitResponse=True)
        return "app: %s, sdk: %s" % (response['appVersion'], response['sdkVersion'])

    @method
    def startInclusion(self):
        """
        start inclusion for 30 secondes
        """
        self.sendMessage('0049', 'FFFC1E')
