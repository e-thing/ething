# coding: utf-8


from .RFLinkNode import RFLinkNode
from ething.core.reg import *
from .helpers import attrMap


@abstract
@attr('interfaces', mode=PRIVATE, default=lambda cls: [get_definition_name(c) for c in cls.__mro__ if get_definition_name(c).startswith('interfaces/')])
class RFLinkGenericSensor(RFLinkNode):

    def _handle_incoming_data(self, protocol, data):
        super(RFLinkGenericSensor, self)._handle_incoming_data(protocol, data)

        if 'TEMP' in data and self.isTypeof('interfaces/Thermometer'):
            self.temperature = float(data['TEMP'])

        if 'HUM' in data and self.isTypeof('interfaces/HumiditySensor'):
            self.humidity = float(data['HUM'])

        if 'BARO' in data and self.isTypeof('interfaces/PressureSensor'):
            self.pressure = float(data['BARO'])

        for k in data:
            if k in attrMap:
                human_readable_name, _ = attrMap[k]
                self.data[human_readable_name] = data[k]

    @classmethod
    def create_dynamic_class(cls, interface_types):

        bases = []
        bases.append(cls)

        for interface_type in interface_types:
            interface_cls = get_registered_class(interface_type)
            bases.append(interface_cls)

        return  type('RFLinkGenericSensor', tuple(bases), {
            '_REGISTER_': False
        })

    @classmethod
    def __instantiate__(cls, data, context):
        dyn_cls = cls.create_dynamic_class(data.get('interfaces', []))
        return dyn_cls(data, context)

