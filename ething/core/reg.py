# coding: utf-8
from .type import *
from .utils import get_cls_methods
from collections import MutableMapping, OrderedDict
import copy
import inspect
from functools import wraps


def _make_default(value, *arg, **kwargs):
  if callable(value):
      return value(*arg, **kwargs)
  return copy.deepcopy(value)



#
# Attributes
#

READ_ONLY = 2
PRIVATE = 4


class _NO_VALUE(object):
    pass

NO_VALUE = _NO_VALUE


class Attribute (MutableMapping):
    
    def __init__(self, name, cls=None, props=None):
        self.name = name
        self.cls = cls
        self._props = dict()
        if props is not None:
            self.update(props)
    
    @property
    def properties (self):
      return self._props
    
    def update(self, *args, **kwargs):
      props = dict(*args, **kwargs)

      for k in props:
          v = props[k]
          if v is NO_VALUE:
            # remove the key
            self._props.pop(k, None)
          else:
            self._props[k] = v

    def __getitem__(self, key):
        return self._props[key]

    def __setitem__(self, key, value):
        self._props[key] = value

    def __delitem__(self, key):
        del self._props[key]

    def __iter__(self):
        return iter(self._props)

    def __len__(self):
        return len(self._props)

    def __repr__(self):
        return "<%s, cls=%s props=%s>" % (self.name, self.cls.__name__, self._props.__repr__())

    def __hash__(self):
        return hash(self.name)
    
    def make_default(self, *arg, **kwargs):
      return _make_default(self.get('default'), *arg, **kwargs)
    
    def toSchema(self, **kwargs):

      data_type = self.get('type')

      if data_type:
        schema = data_type.toSchema(context=kwargs)
      else:
        schema = {}

      if 'description' in self:
        schema['description'] = self.get('description').strip()

      if self.get('mode') == READ_ONLY:
          schema['readOnly'] = True
      
      return schema


def path(name, relative = False):
  def d(cls):

    meta = getattr(cls, '__meta')

    if relative:
      path = meta.get('path')
      if path:
        path += '/'
      path += name
    else:
      path = name
    
    meta['path'] = path

    update_registered_class(cls)

    return cls
  return d

def abstract(cls):
  getattr(cls, '__meta')['abstract'] = True
  return cls

def is_abstract(cls):
  return getattr(cls, '__meta').get('abstract', False)


_attribute_meta_attr = '__meta_attr'


def attr(name=None, **kwargs):
  def d(item):

    if inspect.isclass(item):
      cls = item

      if name is None:
        raise Exception('name argument is mandatory')

      attribute = None

      attributes = getattr(cls, '__meta').get('attributes')

      for i in range(len(attributes)):
        a = attributes[i]
        if a.name == name:
          if a.cls == cls:
            attribute = a
          else:
            # come from a base class, copy it before updating
            attribute = Attribute(name, cls, a.properties.copy())
            attributes[i] = attribute
          attribute.update(kwargs)
          break
      else:
        attribute = Attribute(name, cls = cls, props = kwargs)
        attributes.append(attribute)

      if hasattr(cls, '_attr_modifier_'):
        getattr(cls, '_attr_modifier_')(attribute)

      return cls

    else:
      # computed method
      func = item
      kwargs['compute'] = func
      func_name = func.__name__
      func = ComputedAttrDescriptor(func)
      attr = Attribute(func_name, props=kwargs)
      setattr(func, _attribute_meta_attr, attr)
      return func
  return d


class ComputedAttrDescriptor(object):

  def __init__(self, func):
    self.func = func

  def __get__(self, instance, owner):
    return self.func(instance)


def list_registered_attr(class_or_instance):
  """
  list the attributes of the given class or instance.
  """
  if not inspect.isclass(class_or_instance):
    class_or_instance = type(class_or_instance)

  attributes = getattr(class_or_instance, '__meta', {}).get('attributes', list())

  # look for computed attributes
  for name, func in get_cls_methods(class_or_instance):
    if hasattr(func, _attribute_meta_attr):
      attributes.append(getattr(func, _attribute_meta_attr))

  return attributes


def get_registered_attr(class_or_instance, name):
  for a in list_registered_attr(class_or_instance):
    if a.name == name:
      return a


def has_registered_attr(class_or_instance, name):
  return get_registered_attr(class_or_instance, name) is not None



#
# signals
#

class Signal_(object):

    def __init__(self, signal, cls):
        self.signal = signal
        self.cls = cls


def throw(*args):
  def d(cls):

    signals = getattr(cls, '__meta').get('signals')

    for s in args:
        signal_ = Signal_(s, cls)

        i = 0
        exists = False
        for s_ in signals:
            if s is s_.signal:
                exists = True
                break
            i += 1

        if exists:
            signals[i] = signal_ # replace
        else:
            signals.append(signal_)

    return cls
  return d

def list_registered_signals(class_or_instance):
  """
  list the signals the given class or instance may throw.
  """
  if not inspect.isclass(class_or_instance):
    class_or_instance = type(class_or_instance)
  return getattr(class_or_instance, '__meta', {}).get('signals', [])


#
# Methods
#

_method_meta_attr = '__meta_method'


class MethodDecorator(object):

    def __call__(self, func):
        self.init(func)
        return func

    def init(self, func):
        """
        set the default metadata
        """
        meta = getattr(func, _method_meta_attr, None)
        if meta is None:
          meta = Method._parse(func)
          setattr(func, _method_meta_attr, meta)
        return meta

    # decorators

    def name(self, name):
        def d(func):
            meta = self.init(func)
            meta['name'] = name
            return func
        return d

    def description(self, description):
        def d(func):
            meta = self.init(func)
            meta['description'] = description
            return func
        return d

    def return_type(self, return_type):
        def d(func):
            meta = self.init(func)
            if isinstance(return_type, string_types) and re.search('^[^/]+/[^/]+$', return_type):
                # mime type
                meta['return_type'] = return_type
            else:
                meta['return_type'] = convert_type(return_type)
            return func
        return d

    def arg(self, name, **kwargs):
        def d(func):
            meta = self.init(func)

            if not kwargs.get('enable', True):
                meta['args'].pop(name, None)
            else:
                meta['args'].setdefault(name, {})

                if 'type' in kwargs:
                  kwargs['type'] = convert_type(kwargs['type'])

                meta['args'][name].update(kwargs)

            return func
        return d

method = MethodDecorator()


def _setdefaults(a, b):
  for k in b:
      v = b[k]
      if isinstance(v, dict):
          a.setdefault(k, {})
          _setdefaults(a[k], v)
      else:
          a.setdefault(k, v)


class Method(object):

    def __init__(self, func):
      object.__setattr__(self, '_Method__func', func)
      object.__setattr__(self, '_Method__meta', getattr(func, _method_meta_attr, {}))

    @property
    def meta(self):
        return self.__meta
    
    @property
    def func(self):
        return self.__func

    def __getattr__(self, key):
        return self.__meta.get(key, None)
    
    def __setattr__(self, key, value):
        self.__meta[key] = value
    
    def __call__(self, *args, **kwargs):
      return self.call(*args, **kwargs)

    def call(self, instance, *args, **kwargs):

        if args:
            arg_names = list(self.args)

            for i in range(0, len(args)):

                if i >= len(arg_names):
                    raise ValueError("%s() takes exactly %d arguments" % (
                        self.name, len(arg_names)))

                arg_name = arg_names[i]

                if arg_name in kwargs:
                    raise ValueError(
                        "%s(): got multiple values for keyword argument '%s'" % (self.name, arg_name))

                kwargs[arg_name] = args[i]

        # check the arguments
        for arg_name in kwargs:
            if arg_name not in self.args:
                raise ValueError("%s(): invalid argument '%s'" %
                                 (self.name, arg_name))
            arg_meta = self.args[arg_name]

            if 'type' in arg_meta:
                arg_type = arg_meta['type']

                try:
                  kwargs[arg_name] = arg_type.fromJson(kwargs[arg_name])
                except Exception as e:
                  raise ValueError("%s(): argument '%s' is invalid: %s" % (self.name, arg_name, str(e)))

        # check missing argument !
        for arg_name in self.args:
            arg_meta = self.args[arg_name]
            if arg_name not in kwargs:
                if ('default' not in arg_meta) or arg_meta.get('required', False):
                    raise ValueError("%s(): missing argument '%s'" %
                                     (self.name, arg_name))
                else:
                    arg_type = arg_meta['type']
                    default_value = arg_type.toJson(_make_default(arg_meta.get('default')))
                    kwargs[arg_name] = default_value

        if self.bounded:
            if hasattr(instance, self.func_name):
                res = getattr(instance, self.func_name)(**kwargs)
            else:
                res = self.__func(instance, **kwargs)
        else:
            res = self.__func(**kwargs)

        return res

    def toSchema(self, **kwargs):
        schema = {
            'type': 'function'
        }

        required = []
        arguments = OrderedDict()
        for arg_name in self.args:
            arg_meta = self.args[arg_name]

            if ('default' not in self.args[arg_name]) or self.args[arg_name].get('required', False):
                required.append(arg_name)

            arg_type = arg_meta.get('type', String())

            arg_schema = arg_type.toSchema(context=kwargs)

            if 'description' in arg_meta:
              arg_schema['description'] = arg_meta.get('description').strip()

            if 'default' in arg_meta:
              try:
                arg_schema['default'] = arg_type.toJson(arg_type.set(_make_default(arg_meta.get('default')), context=kwargs), context=kwargs)
              except Exception:
                pass

            arguments[arg_name] = arg_schema

        schema['required'] = required
        schema['arguments'] = arguments

        if self.description:
          schema['description'] = self.description

        if isinstance(self.return_type, Type):
            schema['return'] = self.return_type.toSchema(context=kwargs)
        else:
            schema['return'] = self.return_type

        return schema
    
    def bound_to(self, instance):
      return BoundMethod(self.__func, instance)
  
    @staticmethod
    def inherit(func, orig):
      """
      makes func defaults from orig (no overwritting)
      """
      meta = method.init(func)
      _setdefaults(meta, getattr(orig, _method_meta_attr, {}))
    
    @staticmethod
    def _parse(func):
        """
        extract some metadata from a method
        """
        name = func.__name__
        description = func.__doc__ or ''

        description = description.strip()

        var_count = func.__code__.co_argcount
        var_names = func.__code__.co_varnames[:var_count]
        var_defaults = func.__defaults__ or ()

        default_offset = len(var_names) - len(var_defaults)

        meta = {}

        meta['args'] = OrderedDict()

        for i in range(0, len(var_names)):  # skip self argument
            arg_name = var_names[i]

            if arg_name == 'self':
                meta['bounded'] = True
                continue

            if arg_name == "args" or arg_name == "kwargs":
                continue

            has_default = (i >= default_offset)

            meta['args'].setdefault(arg_name, {})

            if has_default:
              default = var_defaults[i - default_offset] if has_default else None
              meta['args'][arg_name]['default'] = default
              meta['args'][arg_name]['type'] = get_type_from_value(default)

        if description:
            meta['description'] = description

        meta['name'] = name
        meta['func_name'] = name

        return meta


class BoundMethod (Method):

  def __init__(self, func, instance):
    super(BoundMethod, self).__init__(func)
    self._instance = instance
  
  def call(self, *args, **kwargs):
    return super(BoundMethod, self).call(self._instance, *args, **kwargs)


def list_registered_methods(class_or_instance):
  """
  list the methods of the given class or instance.
  """

  cls = class_or_instance
  instance = None

  if not inspect.isclass(class_or_instance):
    cls = type(class_or_instance)
    instance = class_or_instance

  methods = list()
  
  # list all methods attached to this device
  for name, func in get_cls_methods(cls):
      if hasattr(func, _method_meta_attr):
        methods.append(Method(func) if instance is None else BoundMethod(func, instance))
  
  return methods

def get_registered_methods(class_or_instance, name):
  for a in list_registered_methods(class_or_instance):
    if a.name == name:
      return a

def has_registered_methods(class_or_instance, name):
  return get_registered_methods(class_or_instance, name) is not None



#
# Globals
#

def is_meta_class(cls):
    return hasattr(cls, '__meta')

registered_cls = OrderedDict()

def list_registered_classes():
    return registered_cls.values()

def is_registered_class(cls):
    return is_meta_class(cls) and registered_cls.get(get_definition_pathname(cls)) is cls

def get_registered_class(name):
    return registered_cls.get(name)

def register_class(cls):
    if getattr(cls, '_REGISTER_', True):

        cls_name = get_definition_pathname(cls)
        if cls_name in registered_cls:
            raise Exception('A class with the name "%s" already exists: %s' % (cls_name, registered_cls.get(cls_name)))

        registered_cls[cls_name] = cls

def update_registered_class(cls):
    cls_name = get_definition_pathname(cls)
    if cls_name not in registered_cls:
        for n in list(registered_cls):
            c = registered_cls.get(n)
            if cls is c:
                del registered_cls[n]
                registered_cls[cls_name] = cls


class MetaReg(type):

    """MetaReg metaclass"""

    def __new__(meta, name, bases, dct):
      cls = type.__new__(meta, name, bases, dct)

      inherited_meta = getattr(cls, '__meta', {})

      # attributes
      extended_attributes = []
      for b in reversed(bases):
        for attribute_b in list_registered_attr(b):

          attribute = None
          i = 0
          for a in extended_attributes:
            if a.name == attribute_b.name:
              attribute = a
              break
            i += 1

          if attribute is None:
              extended_attributes.insert(0, attribute_b)
          else:
            # copy it before updating
            copy = Attribute(attribute.name, cls, attribute.properties.copy())
            copy.update(attribute_b.properties)
            extended_attributes[i] = copy

      # signals:
      extended_signals = []
      for b in reversed(bases):
          for signal_b_ in list_registered_signals(b):

              exists = False
              i = 0
              for s_ in extended_signals:
                  if s_.signal is signal_b_.signal:
                      exists = True
                      break
                  i += 1

              if not exists:
                  extended_signals.insert(0, signal_b_)
              else:
                # replace
                extended_signals[i] = signal_b_

      setattr(cls, '__meta', {
        'attributes': extended_attributes,
        'signals': extended_signals,
        'abstract': False,
        'path': inherited_meta.get('path', '')
      })

      # methods

      for m in list_registered_methods(cls):
        if m.cls is None:
          m.cls = cls

      for base in bases:
        
        base_m = [m.func for m in list_registered_methods(base)]
        cls_m = [i[1] for i in get_cls_methods(cls)]
        for b_m in base_m:
            if b_m not in cls_m:
                #print('overloading %s' % b_m.__name__)
                # find the overloaded method in cls (same name)
                f_ovl = None
                for c_m in cls_m:
                    if c_m.__name__ == b_m.__name__:
                        f_ovl = c_m
                        break
                if f_ovl is not None:
                    # this method has been overloaded by the class cls
                    Method.inherit(f_ovl, b_m)
                    f_ovl.cls = cls

      # globals
      register_class(cls)

      return cls


def get_definition_pathname(cls):
  """
  returns the definition pathname for the given class or instance (e.g. "#/resources/Resource")
  """
  name = cls.__name__
  meta = getattr(cls, '__meta')
  path = meta.get('path')
  if path:
      return '%s/%s' % (path, name)
  else:
      return name


def build_schema(cls, root=False, **kwargs):

  if not inspect.isclass(cls):
    cls = type(cls)

  flatted = kwargs.get('flatted', True)
  helper = kwargs.get('helper', None)
  subclass = kwargs.get('subclass', None)
  skip = kwargs.get('skip') or ()
  no_methods = kwargs.get('no_methods', False)
  no_signals = kwargs.get('no_signals', False)

  if not flatted and not root:
      return {
          '$ref': '#/' + get_definition_pathname(cls)
      }
  
  schema = {
      "type": "class",
      "properties": OrderedDict(),
      "additionalProperties": False
  }
  attributes = list_registered_attr(cls)

  required = []

  description = cls.__doc__ or ''
  description = description.strip()
  if description:
    schema['description'] = description

  if not no_signals:
      signals = []
      for signal_ in list_registered_signals(cls):
          if (not flatted) and cls is not signal_.cls:
              continue
          signals.append(signal_.signal.__name__)
      if len(signals) > 0:
          schema['signals'] = signals

  for attribute in attributes:
    mode = attribute.get('mode')
    name = attribute.name
    data_type = attribute.get('type')

    if (not flatted) and cls is not attribute.cls:
      continue

    if mode == PRIVATE:
      continue

    attr_schema = attribute.toSchema(**kwargs)

    if mode != READ_ONLY:
        if 'default' in attribute:
            try:
              attr_schema['default'] = data_type.toJson(attribute.make_default(cls), context=kwargs)
            except:
              pass
        else:
          required.append(name)
    
    if callable(helper):
      if helper(schema=attr_schema, name=name, attribute=attribute) is False:
        continue
    
    schema['properties'][name] = attr_schema
  
  schema['required'] = required

  if not no_methods:
    methods = list_registered_methods(cls)

    if methods:
        # schema['type'] = 'class'
        schema['methods'] = OrderedDict()

        for method in methods:

          if (not flatted) and method.cls is not cls:
            continue

          schema['methods'][method.name] = method.toSchema(**kwargs)

  if not flatted:
    all_of = []

    for b in cls.__bases__:
      if subclass is not None and not issubclass(b, subclass):
          continue
      if b in skip:
          continue
      if is_registered_class(b):
        all_of.append({
          '$ref': '#/' + get_definition_pathname(b)
        })
    
    if len(all_of) > 0:
      all_of.append(schema)
      schema = {
        'allOf': all_of
      }
  
  if is_abstract(cls):
    schema['virtual'] = True

  return schema


def build_schema_definitions(**kwargs):
  """
  returns a dictionnarie containing the json schema of all the registered class
  """

  definitions = OrderedDict()

  definitions['interfaces'] = OrderedDict()

  subclass = kwargs.get('subclass')
  skip = kwargs.get('skip') or ()

  for cls in list_registered_classes():

    if subclass is not None and not issubclass(cls, subclass):
        continue

    if cls in skip:
        continue

    meta = getattr(cls, '__meta')
    path = meta.get('path')

    schema = build_schema(cls, flatted = False, root = True, **kwargs)

    rel_def = definitions
    if path:
      for path_item in path.split('/'):
        if path_item not in rel_def:
          rel_def[path_item] = OrderedDict()
        rel_def = rel_def[path_item]
    
    rel_def[cls.__name__] = schema
  
  return definitions



