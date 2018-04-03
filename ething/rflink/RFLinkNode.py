

from ething.Device import Device, method, interface, attr, isString, isNone, isEnum
from ething.interfaces import Switch, Light
import RFLink



meta = [
    ('CMD',('door' , 'motion'),'getState','return the current state', 'bool'),
    ('RAIN',('weatherStation'),'getRain','return current rain level (in mmm)', 'float'),
    ('RAINRATE',('weatherStation'),'getRainRate','return current rain rate (in mmm/h)', 'float'),
    ('WINSP',('weatherStation'),'getWindSpeed','return current wind speed (in km/h)', 'float'),
    ('AWINSP',('weatherStation'),'getAverageWindSpeed','return current average wind speed (in km/h)', 'float'),
    ('WINGS',('weatherStation'),'getWindGust','return current wind gust (in km/h)', 'float'),
    ('WINDIR',('weatherStation'),'getWindDirection','return current wind direction (in degrees)', 'float'),
    ('WINCHL',('weatherStation'),'getWindChill','return current wind chill (in degree Celsius)', 'float'),
    ('WINTMP',('weatherStation'),'getWindTemperature','return current wind temperature (in degree Celsius)', 'float'),
    ('TEMP',('weatherStation','thermometer'),'getTemperature','return current temperature (in degree Celsius)', 'float'),
    ('HUM',('weatherStation','thermometer'),'getHumidity','return current humidity (in %)', 'float'),
    ('BARO',('weatherStation','thermometer'),'getPressure','return current atmospheric pressure (in Pa)', 'float'),
    ('UV',('weatherStation','thermometer'),'getUV','return current UV intensity', 'float'),
    ('LUX',('weatherStation','thermometer'),'weatherStation','getLUX','return current light intensity', 'float'),
    ('HSTATUS',('weatherStation'),'getHygroStatus','return current hygrometry status', 'string'),
    ('BFORECAST',('weatherStation'),'getForecast','return forecast', 'string'),
    ('WATT',('multimeter'),'getWatt','return the power (in Watt)', 'float'),
    ('KWATT',('multimeter'),'getWatt','return the power (in Watt)', 'float'),
    ('CURRENT',('multimeter'),'getCurrent','return the current phase 1 (in A)', 'float'),
    ('CURRENT2',('multimeter'),'getCurrent2','return the current phase 2 (in A)', 'float'),
    ('CURRENT3',('multimeter'),'getCurrent3','return the current phase 3 (in A)', 'float'),
    ('VOLT',('multimeter'),'getVoltage','return the voltage (in V)', 'float'),
    ('FREQ',('multimeter'),'getFrequency','return the frequency (in Hz)', 'float'),
    ('PF',('multimeter'),'getPowerFactor','return the power factor (between -1 and 1)', 'float'),
    ('ENERGY',('multimeter'),'getEnergy','return the instant energy (in watt hour)', 'float')
    
]


@attr('nodeId', validator = isString(allow_empty=False), description="The hardware id of the node.")
@attr('subType', validator = isString() & isEnum(RFLink.subTypes), description="The subtype of the device, ie: thermometer, switch, ...")
@attr('protocol', validator = isString(allow_empty=False), description="The protocol name of the node.")
@attr('switchId', validator = isNone() | isString(allow_empty=False), description="The switch id of the node. Only available for switch/door/motion subtypes.")
@attr('createdBy', required = True)
class RFLinkNode(Device):

    
    
    @property
    def gateway (self):
        return self.createdBy
    
    def __setattr__ (self,    name, value ):
        super(RFLinkNode, self).__setattr__(name, value)
        
        if name == 'subType':
            self.update_interface(False)
    
    def dynamic_interface(self):
        
        subType = self.subType
        
        if subType == 'switch' or subType == 'light':
            
            interface.inherit(self, Switch if subType == 'switch' else Light)
            
            @method.bind_to(self)
            def set_state(self, state):
                value = 'ON' if state else 'OFF'
                if self.gateway.sendMessage("10;%s;%s;%s;%s;" % (self.protocol, self.nodeId, self.switchId, value)): # 10;NewKaku;00c142;1;OFF
                    self.store('state', True)
            
        
        else:
        
            def create_get_method(attr_name, name, description, return_type):
                @method.bind_to(self)
                @method.name(name)
                @method.description(description)
                @method.return_type(return_type)
                def get(self):
                    return self.getData(attr_name)
                return get
            
            for m in meta:
                if subType in m[1]:
                    attr_name = RFLink.getAttrName(m[0])
                    if self.hasData(attr_name):
                        create_get_method(attr_name, m[2], m[3], m[4])
    
    
    # functions used by controller
    @staticmethod
    def createDeviceFromMessage (self, subType, protocol, args, gateway):
        
        return RFLinkNode.create(gateway.ething, {
            'nodeId' : args['ID'],
            'switchId' : RFLink.convertSwitchId(args['SWITCH']) if 'SWITCH' in args else None,
            'protocol' : protocol,
            'subType' : subType,
            'name' : subType+'-'+args['ID'],
            'createdBy': gateway
        })
    
    
    def processMessage (self, protocol, args):
        
        # data decoding :
        decoded = {}
        
        for attr in args:
            if attr in RFLink.attrMap:
                
                name, converter, store = RFLink.attrMap[attr]
                value = converter(args[attr]) if converter else args[attr]
                
                if name == 'battery':
                    self.battery = value
                
                if store == RFLink.STORE_SEPARATE:
                    self.store(name, value)
                elif store == RFLink.STORE:
                    decoded[name] = value
        
        if decoded:
            self.store('data', decoded)
        
        self.save()
        
    
    
    def storeData(self, data):
        
        d = {}
        
        for attr in args:
            if attr in RFLink.attrMap:
                d[RFLink.getAttrName(attr)] = RFLink.convertAttrValue(attr, args[attr])
        
        if d:
            self.setData(d)
            self.storeDataInTable(d)
            
            self.dispatchSignal(DeviceDataSet.emit(self, d))
    


if __name__ == '__main__':
    
    thermometer = RFLinkNode(None, {
        '_id': '456huij',
        'name': 'toto.dev',
        'type': 'RFLinkNode',
        'subType' : 'thermometer',
        'data':{
            'temperature': 45,
            'humidity': 23
        },
        'nodeId' : None,
        'protocol' : None,
        'switchId' : None
    })
    
    #print node.type
    print thermometer.interface.toJson()
    
    print thermometer.getTemperature()
    print thermometer.getHumidity()
    
    
    
    switch = RFLinkNode(None, {
        '_id': '456huij',
        'name': 'toto.dev',
        'type': 'RFLinkNode',
        'subType' : 'switch',
        'data':{
            'state': True
        },
        'nodeId' : 'ff',
        'protocol' : 'ff',
        'switchId' : None
    })
    
    
    #print node.type
    print switch.interface.toJson()
    
    print switch.getState()
    
    
    
    
    
    

