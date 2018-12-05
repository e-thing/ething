# coding: utf-8


from .MihomeBase import MihomeBase
from ething.core.reg import *
import json


@abstract
@attr('voltage', type=Number(), mode=READ_ONLY, default=0, description = 'the voltage of the battery if any')
class MihomeDevice(MihomeBase):
    """
    Mihome Device base class
    """

    def _get_gateway(self):
        return self.createdBy

    def processAttr(self, name, value):
        pass  # to be implemented

    def _processData(self, response):

        data = json.loads(response['data'])

        if isinstance(data, dict):

            for k in data:

                value = data[k]

                if k == 'voltage':
                    voltage = int(value)/1000.  # volt
                    max_volt = 3.300
                    min_volt = 2.800
                    voltage = min(voltage, max_volt)
                    voltage = max(voltage, min_volt)
                    percent = ((voltage - min_volt) / (max_volt - min_volt)) * 100
                    self.voltage = voltage
                    self.battery = round(percent)
                else:
                    self.processAttr(k, value)

