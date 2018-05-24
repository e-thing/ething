# coding: utf-8


from ething.Device import Device, method, attr, abstract, isString
import json


@abstract
@attr('sid', validator=isString(allow_empty=False), description="The uniq sid of the device")
class MihomeDevice(Device):
    """
    Mihome Device base class
    """

    @property
    def gateway(self):
        return self.createdBy

    def processAttr(self, name, value):
        pass  # to be implemented

    def processData(self, response):

        data = json.loads(response['data'])

        if isinstance(data, dict):

            for k in data:

                value = data[k]

                if k == 'voltage':
                    self.store('voltage', int(value)/1000.)  # volt
                else:
                    self.processAttr(k, value)

    def sendCommand(self, cmd):
        return self.gateway.sendCommand(cmd)
