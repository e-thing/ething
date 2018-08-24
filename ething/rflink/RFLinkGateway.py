# coding: utf-8


from ething.Device import Device
from ething.reg import *
from ething.Process import get_process


@abstract
@attr('version', default=None, mode=READ_ONLY, description="The version of the RFLink library used.")
@attr('revision', default=None, mode=READ_ONLY, description="The revision number of the RFLink library used.")
@attr('build', default=None, mode=READ_ONLY, description="The build number of the RFLink library used.")
@attr('inclusion', default=False, type=Boolean(),  description="If true, new devices will be automatically created.")
class RFLinkGateway(Device):

    @property
    def controller(self):
        return get_process('rflink.%s' % self.gateway.id)

    def getNodes(self, filter=None):
        def _filter (r):
            if r.createdBy == self and r.isTypeof('resources/RFLinkNode'):
                if filter:
                    return filter(r)
                return True
            return False

        return self.ething.find(_filter)

    def getNode(self, filter):

        def _filter (r):
            if r.createdBy == self and r.isTypeof('resources/RFLinkNode'):
                if filter:
                    return filter(r)
                return True
            return False

        return self.ething.findOne(_filter)

    def removeAllNodes(self):
        # remove all the nodes attached to it !
        for node in self.getNodes():
            node.remove()

    def remove(self, removeChildren=False):

        # remove all the nodes attached to it !
        self.removeAllNodes()

        # remove the resource
        super(RFLinkGateway, self).remove(removeChildren)

    @method.arg('message', type=String(allow_empty=False))
    def sendMessage(self, message):
        """
        send a message.
        """
        self.controller.send(message)

    def reboot(self):
        """
        reboot the gateway.
        """
        self.controller.send("10;REBOOT;")

    @method.return_type('text/plain')
    def getVersion(self):
        """
        get the version of the gateway.
        """
        result = self.controller.send("10;VERSION;", response = 'BUILD=') # VER=1.1;REV=46;BUILD=0c
        result.wait()

        if result.error:
            raise Exception(str(result.error))

        return result.data.split(';', 2)[-1]
