# coding: utf-8


from .MihomeDevice import MihomeDevice
from ething.core.interfaces import DoorSensor


class MihomeMagnet(MihomeDevice, DoorSensor):
    """
    Mihome door Sensor.
    """

    def processAttr(self, name, value):

        if name == 'status':
            self._state = value == "open"

