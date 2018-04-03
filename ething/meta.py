import sys
import inspect
from collections import OrderedDict


resource_classes = {}

def get_resource_class(name):
    if name in resource_classes:
        return resource_classes[name]
    else:
        return None

class MetaResource(type):
    
    """Resource metaclass"""
    
    def __init__(cls, nom, bases, dict):
        type.__init__(cls, nom, bases, dict)
        resource_classes[nom] = cls


class InterfaceDecorator(object):
    
    def __call__(self, cls):
        self.init(cls)
        return cls
    
    def __parse(self, cls):
        """
        extract some metadata from a class
        """
        name = cls.__name__
        description = cls.__doc__ or ''
        
        description = description.strip()
        
        meta = {}
        
        if description:
            meta['description'] = description
        
        meta['name'] = name
        meta['func_name'] = name
        
        return meta
    
    
    def init(self, cls):
        """
        set the default metadata
        """
        if not getattr(cls, 'meta', None):
            #print "new interface", cls.__name__
            setattr(cls, 'meta', self.__parse(cls))
            
            interface_name = cls.meta['name']
            for c_n, c_m in self.__list_methods_with_meta(cls):
                c_m.meta.setdefault('interfaces', [])
                c_m.meta['interfaces'].append(cls.meta['name'])
            
    
    def __list_methods(self, cls):
        m = []
        for attr in dir(cls):
            try:
                func = getattr(cls,attr)
            except:
                continue
            if callable(func):
                if hasattr(func, 'im_func'):
                    f = func.im_func # https://docs.python.org/2.4/lib/typesmethods.html
                elif hasattr(func, '__func__'):
                    f = func.__func__
                else:
                    f = func
                m.append((attr, f))
        return m
    
    def __list_methods_with_meta(self, cls):
        return [a for a in self.__list_methods(cls) if getattr(a[1], 'meta', None)]
    
    def inherit(self, cls, base = None, filter = None):
        """
        make the class cls derive from one or more base classes 
        a filter {function(method)} can be provided to filter some methods
        """
        
        
        
        if base is None:
            base = cls.__bases__
        
        if isinstance(base, list) or isinstance(base, set) or isinstance(base, tuple):
            for b in base:
                self.inherit(cls, b, filter = filter)
            return
        
        is_instance = not inspect.isclass(cls)
        
        #print "inherit interface", cls.__class__.__name__ if is_instance else cls.__name__, base.__name__, cls.meta if hasattr(cls, 'meta') else None
        
        
        if is_instance:
            # dynamic inheritance !
            ii = getattr(cls, '__interfaces', []) + [c for c in base.__mro__ if getattr(c, 'meta', None)]
            object.__setattr__(cls, '__interfaces', list(set(ii)))
        
        
        #print "check inheritance %s -> %s" % (base.__name__, cls.__name__ if hasattr(cls, '__name__') else type(cls).__name__)
        base_m = [i[1] for i in self.__list_methods_with_meta(base)]
        cls_m = [i[1] for i in self.__list_methods(cls)]
        for b_m in base_m:
            
            if filter:
                if not filter(b_m):
                    continue
            
            if b_m not in cls_m:
                # find the overloaded method in cls (same name)
                f_ovl = None
                for c_m in cls_m:
                    if c_m.__name__ == b_m.__name__:
                        f_ovl = c_m
                        break
                if f_ovl is not None:
                    # this method has been overloaded by the class cls
                    #print "%s overloaded" % b_m.__name__
                    method.inherit(f_ovl, b_m)
                else:
                    if is_instance:
                        #print "%s added" % b_m.__name__
                        method.bind_to(cls)(b_m)
        
        
    
    
    def clear(self, instance):
        # remove any dynamic interfaces
        if hasattr(instance, '__interfaces'):
            object.__setattr__(instance, '__interfaces', [])
        
        # remove any dynamic methods
        for name, method in self.__list_methods_with_meta(instance):
            if method.meta.get('dynamic_bound'):
                delattr(instance, name)
    
    # decorators
    
    def name(self, name):
        def d(cls):
            self.init(cls)
            cls.meta['name'] = name
            return cls
        return d
    
    def description(self, description):
        def d(cls):
            self.init(cls)
            cls.meta['description'] = description
            return cls
        return d
    
    def meta(self, **kwargs):
        def d(cls):
            self.init(cls)
            for k in kwargs:
                cls.meta[k] = kwargs[k]
            return cls
        return d


class MethodDecorator(object):
    
    def __init__(self):
        self.p3 = (sys.version_info > (3, 0))
    
    def __call__(self, func):
        self.init(func)
        return func
    
    def __parse(self, func):
        """
        extract some metadata from a method
        """
        name = func.__name__
        description = func.__doc__ or ''
        args = {}
        
        description = description.strip()
        
        var_count = func.__code__.co_argcount
        var_names = func.__code__.co_varnames[:var_count]
        var_defaults = func.__defaults__ or ()
        
        default_offset = len(var_names) - len(var_defaults)
        
        meta = {}
        
        meta['args'] = OrderedDict()
        
        for i in range(0,len(var_names)): # skip self argument
            arg_name = var_names[i]
            
            if arg_name == 'self':
                meta['bounded'] = True
                continue
            
            if arg_name == "args" or arg_name == "kwargs":
                continue
            
            has_default = (i >= default_offset)
            default = var_defaults[i - default_offset] if has_default else None
            arg_type = type(default).__name__ if has_default else None
            
            meta['args'].setdefault(arg_name, {})
            
            if has_default:
                meta['args'][arg_name]['default'] = default
                meta['args'][arg_name]['type'] = arg_type
        
        if description:
            meta['description'] = description
        
        meta['name'] = name
        meta['func_name'] = name
        
        return meta
    
    def init(self, func):
        """
        set the default metadata
        """
        if not hasattr(func, 'meta'):
            #print "new method", func.__name__
            setattr(func, 'meta', self.__parse(func))
    
    def __setdefaults(self,a,b):
        for k in b:
            v = b[k]
            if isinstance(v, dict):
                a.setdefault(k,{})
                self.__setdefaults(a[k], v)
            else:
                a.setdefault(k,v)
    
    def inherit(self, func, orig):
        """
        makes func defaults from orig (no overwritting)
        """
        self.init(func)
        #print "inherit method",func,"from",orig
        self.__setdefaults(func.meta, orig.meta)
    
    
    
    # decorators
    
    def name(self, name):
        def d(func):
            self.init(func)
            func.meta['name'] = name
            return func
        return d
    
    def description(self, description):
        def d(func):
            self.init(func)
            func.meta['description'] = description
            return func
        return d
    
    def return_type(self, return_type):
        def d(func):
            self.init(func)
            func.meta['return_type'] = return_type
            return func
        return d
    
    def arg(self, name, **kwargs):
        def d(func):
            self.init(func)
            
            if not kwargs.get('enable', True):
                func.meta['args'].pop(name, None)
            else:
                func.meta['args'].setdefault(name, {})
                func.meta['args'][name].update(kwargs)
            
            return func
        return d
    
    def bind_to(self, instance):
        def d(func):
            self.init(func)
            func.meta['dynamic_bound'] = True
            object.__setattr__(instance, func.meta['name'], func.__get__(instance, instance.__class__))
            return func
        return d
    
    def meta(self, **kwargs):
        def d(func):
            self.init(func)
            for k in kwargs:
                func.meta[k] = kwargs[k]
            return func
        return d

method = MethodDecorator()
interface = InterfaceDecorator()


type_synonyms = [
    ['int', 'float', 'long', 'double'],
    ['unicode', 'string']
]


class Method(object):
    
    def __init__(self, func, device):
        self.__func = func
        self.__meta = func.meta
        self.__device = device
    
    @property
    def device(self):
        return self.__device
    
    @property
    def meta(self):
        return self.__meta
    
    def __getattr__(self, index):
        return self.__meta.get(index, None)
    
    def call(self, *args, **kwargs):
        
        if args:
            arg_names = self.args.keys()
            
            for i in range(0,len(args)):
                
                if i>= len(arg_names):
                    raise ValueError("%s() takes exactly %d arguments", (self.name, len(arg_names)))
                
                arg_name = arg_names[i]
                
                if arg_name in kwargs:
                    raise ValueError("%s(): got multiple values for keyword argument '%s'" % (self.name, arg_name))
                
                kwargs[arg_name] = args[i]
        
        # check the arguments
        for arg_name in kwargs:
            v = kwargs[arg_name]
            if arg_name not in self.args:
                raise ValueError("%s(): invalid argument '%s'" % (self.name, arg_name))
            arg_meta = self.args[arg_name]
            
            if 'type' in arg_meta:
                read_type = type(v).__name__
                read_types = None
                
                for synonyms in type_synonyms:
                    if read_type in synonyms:
                        read_types = synonyms
                        break
                
                if not read_types:
                    read_types = [read_type]
                
                if arg_meta['type'] not in read_types :
                    raise ValueError("%s(): argument '%s' has wrong type, got %s instead of %s" % (self.name, arg_name,type(v).__name__,arg_meta['type']))
        
        # check missing argument !
        for arg_name in self.args:
            
            if arg_name not in kwargs:
                if ('default' not in self.args[arg_name]) or self.args[arg_name].get('required', False):
                    raise ValueError("%s(): missing argument '%s'" % (self.name, arg_name))
                else:
                    kwargs[arg_name] = self.args[arg_name]['default']
        
        if self.bounded:
            if hasattr(self.device, self.func_name):
                res = getattr(self.device, self.func_name)(**kwargs)
            else:
                res = self.__func(self.device, **kwargs)
        else:
            res = self.__func(**kwargs)
        
        return res
    
    def get_schema(self):
        schema = {
            'type' : 'object',
            'additionalProperties' : False
        }
        
        required = []
        properties = {}
        for arg_name in self.args:
            arg_meta = self.args[arg_name]
            
            if ('default' not in self.args[arg_name]) or self.args[arg_name].get('required', False):
                required.append(arg_name)
            
            arg_schema = {}
            arg_schema.update(arg_meta)
            
            if 'type' in arg_schema:
                if arg_schema['type'] == 'str':
                    arg_schema['type'] = 'string'
            
            properties[arg_name] = arg_schema
        
        
        schema['required'] = required
        schema['properties'] = properties
        
        return schema
    
    def toJson(self):
        return {
            'name': self.name,
            'interfaces': self.interfaces,
            'description': self.description,
            'return': self.return_type,
            'schema': self.get_schema(),
            'device': {
                'type': self.device.type,
                'id': self.device.id
            }
        }

class Interface(object):
    
    def __init__(self, device):
        self.__device = device
        self.build()
    
    @property
    def device(self):
        return self.__device
    
    @property
    def methods(self):
        return self.__methods
    
    @property
    def method_names(self):
        return [x.name for x in self.methods]
    
    @property
    def bases_names(self):
        return [x.meta['name'] for x in self.bases]
    
    @property
    def bases(self):
        return self.__bases
    
    def build(self):
        self.__methods = []
        
        # remove any dynamic methods/interfaces first
        interface.clear(self.device)
        
        # loads dynamic methods first
        self.device.dynamic_interface()
        
        # list all methods attached to this device
        for attr in dir(self.device):
            try:
                func = getattr(self.device, attr)
            except:
                continue
            if hasattr(func, 'meta') and not inspect.isclass(func):
                self.__methods.append(Method(func, self.device))
        
        # list all the interfaces this instance depends one
        self.__bases = [c for c in self.device.__class__.__mro__ if getattr(c,'meta',None)] + getattr(self.device, '__interfaces', [])
        
    
    
    def get_method(self, name):
        for m in self.methods:
            if m.name == name:
                return m
        raise KeyError("%s not found" % name)
    
    def call(self, name, **kwargs):
        return self.get_method(name).call(**kwargs)
    
    def decompose(self):
        j = {}
        
        
        for i in self.bases_names:
            j.setdefault(i, [])
            for m in self.methods:
                if m.interfaces and i in m.interfaces:
                    j[i].append(m.name)
        
        others = [m.name for m in self.methods if not m.interfaces]
        
        if others:
            j['_'] = others
        
        return j
                
            
        
    
    def toJson(self):
        
        j = {
            'interfaces': self.bases_names,
            'methods' : []
        }
        
        for m in self.methods:
            j['methods'].append(m.toJson())
        
        return j
        

class MetaInterface(type):
    
    """MetaInterface metaclass"""
    
    def __init__(cls, nom, bases, dict):
        
        # do not propagate the meta attributes
        if hasattr(cls, 'meta'):
            setattr(cls, 'meta', None) 
        
        # check interface inheritance
        interface.inherit(cls)


class MetaDevice(MetaResource, MetaInterface):
    
    """Device metaclass"""
    
    def __init__(cls, nom, bases, dict):
        MetaResource.__init__(cls, nom, bases, dict)
        MetaInterface.__init__(cls, nom, bases, dict)


class iface(object):
    __metaclass__ = MetaInterface
    


event_classes = {}

def get_event_class(name):
    if name in event_classes:
        return event_classes[name]
    else:
        return None

class MetaEvent(type):
    
    """Event metaclass"""
    
    def __init__(cls, nom, bases, dict):
        type.__init__(cls, nom, bases, dict)
        event_classes[nom] = cls


condition_classes = {}

def get_condition_class(name):
    if name in condition_classes:
        return condition_classes[name]
    else:
        return None

class MetaCondition(type):
    
    """Condition metaclass"""
    
    def __init__(cls, nom, bases, dict):
        type.__init__(cls, nom, bases, dict)
        condition_classes[nom] = cls



action_classes = {}

def get_action_class(name):
    if name in action_classes:
        return action_classes[name]
    else:
        return None

class MetaAction(type):
    
    """Action metaclass"""
    
    def __init__(cls, nom, bases, dict):
        type.__init__(cls, nom, bases, dict)
        action_classes[nom] = cls
