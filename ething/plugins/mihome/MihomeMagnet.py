# coding: utf-8


from .MihomeDevice import MihomeDevice
from ething.interfaces import DoorSensor


class MihomeMagnet(MihomeDevice, DoorSensor):
    """
    Mihome door Sensor.
    """

    @classmethod
    def isvalid(cls, gateway, model):
        return model in ['magnet', 'sensor_magnet', 'sensor_magnet.aq2']

    def process_attr(self, name, value):

        if name == 'status':
            self.state = value == "open"
