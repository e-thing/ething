# coding: utf-8

from ething.Device import Device
from ething.reg import *
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
        q = {
            'extends': 'resources/MySensorsSensor',
            'createdBy': self.id
        }

        if filter is not None:
            q = {
                '$and': [q, filter]
            }

        return self.ething.find(q)

    def getSensor(self, sensorId):
        return self.ething.findOne({
            'extends': 'resources/MySensorsSensor',
            'createdBy': self.id,
            'sensorId': sensorId
        })

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

    @method.arg('sensorId', type='integer', minimum=0, maximum=255)
    @method.arg('type', type='integer', minimum=0, maximum=4)
    @method.arg('subtype', type='integer', minimum=0, maximum=255)
    @method.arg('payload', type='string', maxLength=25)
    @method.return_type('application/json')
    def send(self, sensorId, type, subtype, payload=''):
        """
        send a message.
        """
        return self.gateway.send(self.nodeId, sensorId, type, subtype, payload, smartSleep = self.smartSleep, ack = self.ackEnabled)

    @method
    def reboot(self):
        """
        Request this node to reboot
        """
        self.send(INTERNAL_CHILD, INTERNAL, I_REBOOT)
