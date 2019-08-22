# coding: utf-8


from .RFLinkNode import RFLinkNode
from ething.reg import *
from .helpers import attrMap


@dynamic
class RFLinkGenericSensor(RFLinkNode):

    def _handle_incoming_data(self, protocol, data):
        super(RFLinkGenericSensor, self)._handle_incoming_data(protocol, data)

        if 'TEMP' in data and self.typeof('interfaces/Thermometer'):
            self.temperature = float(data['TEMP'])

        if 'HUM' in data and self.typeof('interfaces/HumiditySensor'):
            self.humidity = float(data['HUM'])

        if 'BARO' in data and self.typeof('interfaces/PressureSensor'):
            self.pressure = float(data['BARO'])

        for k in data:
            if k in attrMap:
                human_readable_name, _ = attrMap[k]
                self.data[human_readable_name] = data[k]

