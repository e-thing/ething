# coding: utf-8

from ething.core.Device import Device
from ething.core.reg import *
from .helpers import *


@attr('nodeId', type=Integer(min=1, max=254), description="The id of the node.")
@attr('sketchName', default='', mode=READ_ONLY, description="The name of the sketch uploaded.")
@attr('sketchVersion', default='', mode=READ_ONLY, description="The version of the sketch uploaded.")
@attr('smartSleep', type=Boolean(), default=False, description="SmartSleep feature enabled for this node.")
@attr('firmware', default=None, mode=READ_ONLY)
@attr('libVersion', default=None, mode=READ_ONLY, description="The version of the MySensors library used.")
@attr('ackEnabled', type=Boolean(), default=False, description="If set, every message sent must be acknowledged.")
@attr('createdBy', required=True)
class MySensorsNode(Device):
    """
    MySensorsNode Device resource representation. This device is normally automatically created by a MySensorsGateway instance.
    """

    @property
    def controller(self):
        return self.gateway.controller

    @property
    def gateway(self):
        return self.createdBy

    def _save(self, dirty_attrs):
        super(MySensorsNode, self)._save(dirty_attrs)

        if get_registered_attr(self, 'battery') in dirty_attrs:
            # update the battery value to the attached sensors too
            for sensor in self.getSensors():
                sensor.battery = self.battery
                sensor.save()

    def getSensors(self, filter=None):

        def _filter (r):
            if r.createdBy == self and r.isTypeof('resources/MySensorsSensor'):
                if filter:
                    return filter(r)
                return True
            return False

        return self.core.find(_filter)

    def getSensor(self, sensorId):
        return self.core.findOne(lambda r: r.isTypeof('resources/MySensorsSensor') and r.createdBy == self and r.sensorId == sensorId)

    def removeAllSensors(self):
        # remove all the nodes attached to it !
        for sensor in self.getSensors():
            sensor.remove()

    def remove(self, removeChildren=False):

        # remove all the sensors attached to it !
        self.removeAllSensors()

        # remove the resource
        super(MySensorsNode, self).remove(removeChildren)

    # @method.arg('firmware', type='string', format='binary', minLength=1, description='only *.hex files must be uploaded !')
    def updateFirmware(self, firmware):
        """
        OTA (on the air) firmware update.
        """
        return self.controller.update_firmware(self, firmware)

    @method.arg('sensorId', type=Integer(min=0, max=255), required=True)
    @method.arg('type', type=Integer(min=0, max=4), required=True)
    @method.arg('subtype', type=Integer(min=0, max=255), required=True)
    @method.arg('payload', type=String(maxLength=25), default="")
    @method.return_type('application/json')
    def send(self, sensorId, type, subtype, payload=None, **kwargs):
        """
        send a message.
        """
        kwargs.setdefault('smartSleep', self.smartSleep)
        kwargs.setdefault('ack', self.ackEnabled)
        return self.gateway.send(self.nodeId, sensorId, type, subtype, payload, *kwargs)

    @method
    def reboot(self):
        """
        Request this node to reboot
        """
        self.send(INTERNAL_CHILD, INTERNAL, I_REBOOT)
