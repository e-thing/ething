# coding: utf-8


from ething.Device import Device, method, attr, abstract, isString, isBool, isNone, READ_ONLY


@abstract
@attr('version', default=None, mode=READ_ONLY, description="The version of the RFLink library used.")
@attr('revision', default=None, mode=READ_ONLY, description="The revision number of the RFLink library used.")
@attr('build', default=None, mode=READ_ONLY, description="The build number of the RFLink library used.")
class RFLinkGateway(Device):

    def getNodes(self, filter=None):
        q = {
            'type': 'RFLinkNode',
            'createdBy': self.id
        }

        if filter is not None:
            q = {
                '$and': [q, filter]
            }

        return self.ething.find(q)

    def getNode(self, filter):
        return self.ething.findOne({
            '$and': [
                {
                    'type': 'RFLinkNode',
                    'createdBy': self.id
                }, filter
            ]
        })

    def removeAllNodes(self):
        # remove all the nodes attached to it !
        for node in self.getNodes():
            node.remove()

    def remove(self, removeChildren=False):

        # remove all the nodes attached to it !
        self.removeAllNodes()

        # remove the resource
        super(RFLinkGateway, self).remove(removeChildren)

    @method.arg('message', type='string', minLength=1)
    @method.return_type('text/plain')
    def sendMessage(self, message):
        """
        send a message.
        """
        return self.ething.rpc.request('device.rflink.send', self.id, message)

    # send a message and wait for the response.
    # note: not all request has a response !

    def sendMessageWaitResponse(self, message):
        return self.ething.rpc.request('device.rflink.sendWaitResponse', self.id, message)

    def reboot(self):
        """
        reboot the gateway.
        """
        self.sendMessage("10;REBOOT;")

    @method.return_type('text/plain')
    def getVersion(self):
        """
        get the version of the gateway.
        """
        error, _, resp = self.sendMessageWaitResponse("10;VERSION;")
        if error:
            raise Exception(error)
        return resp.split(';', 2)[-1]

    @method
    def startInclusion(self):
        """
        Put this gateway into inclusion mode. Unknown devices will be added automatically.
        """
        self.setData("inclusion", True)

    @method
    def stopInclusion(self):
        """
        Quit the inclusion mode for this gateway.
        """
        self.setData("inclusion", False)
