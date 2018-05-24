# coding: utf-8
from future.utils import string_types


from ething.Device import Device, method, attr, abstract, isString
from ething.utils import pingable
from ething.interfaces import Light
import json


@abstract
@pingable()
@attr('host', validator=isString(allow_empty=False), description="The ip address or hostname of the device to connect to.")
class YeelightDevice (Device, Light):

    def storeData(self, data):

        if "power" in data:
            self.store('state', 'on' in data["power"].lower())

    def sendMessage(self, message):
        if isinstance(message, string_types):
            message = json.loads(message)
        return self.ething.rpc.request('device.yeelight.send', self.id, message)

    # send a message and wait for the response.
    # note: not all request has a response !

    def sendMessageWaitResponse(self, message):
        if isinstance(message, string_types):
            message = json.loads(message)
        return self.ething.rpc.request('device.yeelight.sendWaitResponse', self.id, message)

    # def getState(self):
    #    error, message, response = self.sendMessage('{"method":"get_prop","params":["power"]}', waitResponse = True)
    #    return 'on' in response[0].lower()

    def setState(self, state):
        self.sendMessage('{"method":"set_power", "params":["%s", "smooth", 500]}' % (
            'on' if state else 'off'))
