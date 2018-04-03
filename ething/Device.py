

from ething.Resource import Resource
from ething.rule.event.LowBatteryDevice import LowBatteryDevice
from ething.rule.event.DeviceConnected import DeviceConnected
from ething.rule.event.DeviceDisconnected import DeviceDisconnected
from ething.Helpers import dict_recursive_update
from meta import MetaDevice, interface, method, Interface, Method
from base import *
import datetime


@attr('battery', validator = isNone() | isInteger(min=0, max=100), default = None, description="The battery level of this device (must be between 0 (empty) and 100 (full) , or null if the device has no battery information).") # 0-100 : the battery level, if None it means that no battery information is provided
@attr('location', validator = isNone() | isString(), default = None, description="The location of this device.")
@attr('connected', validator = isBool(), default = False, description="Set to true when this device is connected.")
@attr('lastSeenDate', validator = isNone() | isInstance(datetime.datetime), default = None, description="Last time this device was reached or made a request.")
@attr('methods', default = [], mode = READ_ONLY, description="The list of the methods available.")
@attr('interfaces', default = [], mode = READ_ONLY, description="A list of intefaces this device inherit")
class Device(Resource):
    
    __metaclass__ = MetaDevice
    
    
    BATTERY_NONE = None
    BATTERY_EMPTY = 0
    BATTERY_LOW   = 10
    BATTERY_HALF  = 50
    BATTERY_FULL  = 100
    
    
    
    def __init__(self, ething, data = None):
        super(Device, self).__init__(ething, data)
        if data is not None: # do not try to load any interfaces when there is no data, ie on resource creation, the interface will be loaded on insertion (cf: _insert()).
            object.__setattr__(self, '_Device__interface', Interface(self))
    
    @property
    def interface(self):
        #if self.__interface is None:
        #    self.__interface = True # avoid some looping ... do not remove
        #    #print "load interface for", self.__class__.__name__
        #    self.__interface = Interface(self)
        return self.__interface
    
    
    def dynamic_interface(self):
        # dynamic methods can be instancied here
        # they will be loaded automatically
        
        """
        # to define a new method
        @method.bind_to(self)
        @method.description("dynamic bounded attached")
        def set_temperature(self, temperature): # self will be replaced by the device instance
            pass
        
        # or if you want to load a full interface
        # just do
        interface.inherit(self, Switch)
        
        """
        
        pass
    
    
    
    # kwargs contains all the table attributes
    def storeDataInTable (self, data, **kwargs):
        
        tableName = kwargs.get('name', 'data')
        
        if not isinstance(data, dict):
            data = {'value' : data}
        
        
        storage = self.ething.findOne({
            'name' : tableName,
            'type' : 'Table',
            'createdBy' : self.id
        })
        
        if not storage:
            # create it !
            storage = self.ething.create('Table', dict_recursive_update({
                'name' : tableName,
                'createdBy': self
            }, kwargs))
        
        
        if storage:
            storage.insert(data)
        
        return storage
    
    
    def store( self, name, value, history = 5000, emit = True ):
        """
        Store some data along with this device.
        Value can be a scalar (number, boolean or string) or a dictionnary (usefull if the information to store cannot be described by a single value).
        If value is a dictionnary, name match the name of the table (if any). A tuple can also be given to split the value into multiple tables (use OrderedDict for the values). 
        For instance, a device acting like a thermometer will store the temperature : device.store('temperature', 12.5).
        The last value is accessible through the resource's data attribute : device.data['temperature']
        If history is True, the value will be saved in a table. You may pass an integer that specify the max length of the table during its creation (else this value is ignored). 
        If emit is True (default), an event will be emitted
        """
        
        if value is None:
            return # nothing to store !
        
        with self:
            
            if not isinstance(value, dict):
                dataset = {name: value}
            else:
                if not value:
                    return # empty dictionnary, nothing to store !
                dataset = value
            
            for k in dataset:
                self.data[k] = dataset[k]
            
            self.setDirtyAttr('data')
            
            if history:
                
                t = []
                
                if isinstance(name, basestring):
                    t.append( (name, dataset) )
                elif name is None:
                    for k in dataset:
                        t.append( (k, {k,dataset[k]}) )
                else:
                    k = dataset.keys()
                    v = dataset.values()
                    for i in range(0, len(name)):
                        t.append( (name[i], {k[i],v[i]}) )
                
                for table_name, table_data in t:
                    
                    storage = self.ething.findOne({
                        'name' : table_name,
                        'type' : 'Table',
                        'createdBy' : self.id
                    })
                    
                    if not storage:
                        
                        maxLength = 5000
                        
                        if isinstance(history, int):
                            maxLength = history if history > 0 else None
                        
                        # create it !
                        storage = self.ething.create('Table', {
                            'name' : table_name,
                            'createdBy': self,
                            'maxLength': maxLength
                        })
                    
                    
                    if storage:
                        storage.insert(table_data)
            
            if emit:
                self.dispatchSignal('DeviceDataSet', self, dataset)
    
    
    def _insert(self, data):
        self.update_interface(False)
        super(Device, self)._insert(data)
    
    
    def setConnectState (self, connected):
        
        connected = bool(connected)
        
        if connected:
            self.lastSeenDate = datetime.datetime.utcnow()
        
        if self.connected != connected:
            self.connected = connected
            
            if connected:
                self.ething.log.debug("device connected %s" % self)
                self.dispatchSignal(DeviceConnected.emit(self))
            else:
                self.ething.log.debug("device disconnected %s" % self)
                self.dispatchSignal(DeviceDisconnected.emit(self))
        
        self.save()
    
    
    
    def update_interface(self, save = True):
        object.__setattr__(self, '_Device__interface', Interface(self))
        self._methods = self.interface.method_names
        self._interfaces = self.interface.bases_names
        if save:
            self.save()
    
    def refresh(self, keepDirtyFields = False):
        super(Device, self).refresh(keepDirtyFields)
        object.__setattr__(self, '_Device__interface', Interface(self))
    
    



