# coding: utf-8


from .RFLinkNode import RFLinkNode
from ething.core.reg import *
from .helpers import attrMap


@abstract
class RFLinkGenericSensor(RFLinkNode):

    def _handle_incoming_data(self, protocol, data):
        super(RFLinkGenericSensor, self)._handle_incoming_data(protocol, data)

        if 'TEMP' in data and self.isTypeof('interfaces/Thermometer'):
            self._temperature = float(data['TEMP'])

        if 'HUM' in data and self.isTypeof('interfaces/HumiditySensor'):
            self._humidity = float(data['HUM'])

        if 'BARO' in data and self.isTypeof('interfaces/PressureSensor'):
            self._pressure = float(data['BARO'])

        for k in data:
            if k in attrMap:
                human_readable_name, _ = attrMap[k]
                self.data[human_readable_name] = data[k]

    @classmethod
    def create_dynamic_class(cls, interface_types):

        bases = set()
        bases.add(cls)

        for interface_type in interface_types:
            interface_cls = get_registered_class(interface_type)
            bases.add(interface_cls)

        return type('RFLinkSensor', tuple(bases), {
            '_REGISTER_': False
        })


    @classmethod
    def unserialize(cls, data, context = None):
        interface_types = list(filter(lambda t: t.startswith('interfaces/'), data.get('extends', [])))
        dyn_cls = cls.create_dynamic_class(interface_types)
        return RFLinkNode.unserialize.__func__(dyn_cls, data, context)

    @classmethod
    def create_class_from_data(cls, protocol, data):

        interfaces = set()

        if 'TEMP' in data:
            interfaces.add('interfaces/Thermometer')
        if 'HUM' in data:
            interfaces.add('interfaces/HumiditySensor')
        if 'BARO' in data:
            interfaces.add('interfaces/PressureSensor')

        if len(interfaces)>0:
            return cls.create_dynamic_class(interfaces)

