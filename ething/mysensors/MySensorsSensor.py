


from ething.Device import Device, attr, Validator, isInteger, isString, ModelAdapter
from ething.meta import interface, method, iface
import interfaces
from ething.Helpers import dict_recursive_update
import MySensors
from ething.rule.event.DeviceDataSet import DeviceDataSet
import inspect


type_to_interface = {}


for iname, iclass in inspect.getmembers(interfaces, inspect.isclass):
    if issubclass(iclass, iface):
        type = 'S_%s' % iname.upper()
        type_to_interface[type] = iclass




class isSensorType(Validator):
    def validate(self, value):
        if MySensors.sensorTypeStr(value) is None:
            raise ValueError('must be a valid integer or a string describing a sensor type')
        return value
    
    def schema(self):
        return {"type":"string"}

class SensorTypeAdapter(ModelAdapter):
    
    def set(self, data_object, data, name, value):
        data[name] = MySensors.sensorTypeInt(value)
    
    def get(self, data_object, data, name):
        return MySensors.sensorTypeStr(data[name])

@attr('sensorId', validator = isInteger(min=0, max=254), description="The id of the sensor.")
@attr('sensorType', validator = (isString(allow_empty=False) | isInteger(min=0)) & isSensorType(), model_adapter = SensorTypeAdapter(), description="The type of the sensor.")
@attr('createdBy', required = True)
class MySensorsSensor (Device):
    """
    MySensorsSensor Device resource representation. This device is normally automatically created by a MySensorsNode instance.
    """
    
    @property
    def node (self):
        return self.createdBy
    
    @property
    def nodeId (self):
        return self.node.nodeId
    
    @property
    def gateway (self):
        return self.node.gateway
    
    
    def __setattr__ (self,    name, value ):
        super(MySensorsSensor, self).__setattr__(name, value)
        
        if name == 'sensorType':
            self.update_interface(False)
    
    def storeData (self, datatype, value):
        
        meta = MySensors.valueTypes.get(datatype)
        
        if meta:
            
            name = meta[1]
            history = meta[3]
            
            if datatype == 'V_UP':
                value = 'up'
            elif datatype == 'V_DOWN':
                value = 'down'
            elif datatype == 'V_STOP':
                value = 'stop'
            
            if isinstance(name, tuple):
                keys = list(name)
                
                if isinstance(value, tuple):
                    values = list(value)
                else:
                    values = [value for _ in range(0,len(keys))]
                
                name = None # a table will be created for every values, the name of the table will correspond to the associated key
                value = dict(zip(keys, values))
            
            self.store(name, value, history)
            
        
    
    
    def storeStream (self, streamtype, data):
        if isinstance(streamtype, int):
            streamtype = MySensors.streamTypeStr(streamtype)
        
        if data and streamtype:
            
            storageName = None
            
            if streamtype == "ST_SOUND":
                storageName = 'sound'
            elif streamtype == "ST_IMAGE":
                storageName = 'image'
            
            
            if storageName:
                
                storage = self.ething.findOne({
                    'name' : storageName,
                    'type' : 'File',
                    'createdBy' : self.id
                })
                
                if not storage:
                    storage = self.ething.create('File', {
                        'name' : storageName,
                        'createdBy': self
                    })
                
                
                if storage:
                    storage.write(data)
                
    
    
    
    
    @method.arg('type', type='integer', minimum=0, maximum=4)
    @method.arg('ack', type='bool', default = False)
    @method.arg('subtype', type='integer', minimum=0, maximum=255)
    @method.arg('payload', type='string', maxLength=25)
    @method.return_type('application/json')
    def sendMessage (self, type, ack, subtype, payload = ''):
        """
        send a message.
        """
        return self.node.sendMessage(self.sensorId, type, ack, subType, payload)
    
    
    def set_value(self, type, value, store = True):
        res = self.sendMessage(MySensors.SET, MySensors.NO_ACK, type, value)
        if res and store:
            self.storeData(type, value)
    
    def get_value(self, type, default = None):
        return self.getData(MySensors.valueTypeToName(type), default)
    
    
    
    def dynamic_interface(self):
        sensorType = self.sensorType
        
        if sensorType in type_to_interface:
            interface.inherit(self, type_to_interface[sensorType], filter = lambda func: ('optional' not in func.meta) or self.hasData(MySensors.valueTypeToName(func.meta['optional'])))
            
    
    
    
    
    
if __name__ == '__main__':
    import json
    
    print "start"
    
    cover = MySensorsSensor(None, {
        '_id': '456huij',
        'name': 'toto.dev',
        'type': 'RFLinkNode',
        'sensorId': 4,
        'sensorType' : 'S_COVER',
        'data':{
            'temperature': 45,
            'humidity': 23,
            'percentage': 10.5
        }
    })
    
    print "start"
    
    #print node.type
    #print cover.interface.method_names
    #print json.dumps(cover.interface.toJson(), indent = 4)
    print cover.getLevel()
    
    print cover.interface.method_names
    print cover.interface.bases_names
    
    
    cover.sensorType = 'S_TEMP'
    
    try:
        cover.update_interface()
    except:
        pass
    
    print cover.interface.method_names
    print cover.interface.bases_names
    
    cover.sensorType = 'S_RGBW_LIGHT'
    
    try:
        cover.update_interface()
    except:
        pass
    
    print cover.interface.method_names
    print cover.interface.bases_names
    print cover.interface.decompose()
    
    #print json.dumps(cover.interface.toJson(), indent = 4)
    


