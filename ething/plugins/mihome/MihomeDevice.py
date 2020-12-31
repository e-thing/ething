# coding: utf-8


from .MihomeBase import MihomeBase
from ething.reg import *
import json


mihome_device_classes = set()


class MihomeDeviceMetaClass(MetaReg):
    def __new__(meta, name, bases, dct):
        cls = MetaReg.__new__(meta, name, bases, dct)

        if not is_abstract(cls):
            mihome_device_classes.add(cls)

        return cls


@abstract
@meta(disable_creation=True)
@attr('voltage', type=Number(), mode=READ_ONLY, default=0, description = 'the voltage of the battery if any')
class MihomeDevice(with_metaclass(MihomeDeviceMetaClass, MihomeBase)):
    """
    Mihome Device base class
    """

    ACTIVITY_TIMEOUT = 1800

    @classmethod
    def isvalid(cls, gateway, model):
        return False

    def _get_gateway(self):
        return self.createdBy

    def process_attr(self, name, value):
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
                    try:
                        self.process_attr(k, value)
                    except:
                        self.logger.exception('unable to parse %s', response['data'])

