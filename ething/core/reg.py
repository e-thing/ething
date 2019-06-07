# coding: utf-8
from future.utils import with_metaclass, string_types, integer_types, text_type, binary_type
from collections import MutableMapping, OrderedDict, Mapping
import copy
import inspect
from abc import ABCMeta
import re
import random
import string
from .utils import getmembers


def format_label(name):
    """make user friendly labels"""

    if re.search('^[a-zA-Z]+$', name):
        matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', name)
        return ' '.join([m.group(0) for m in matches])

    if re.search('^[_a-zA-Z]+$', name):
        return ' '.join(name.split('_'))

    return name


def extract_from_docstring(docstr):
    if not docstr:
        return

    l = 0
    l_valid = 0
    b_only_blank = True

    lines = docstr.splitlines()
    for line in lines:
        line = line.strip()
        if line == '':
            l_valid = l
        elif re.search('^\s*[a-zA-Z0-9]', line) and not re.search(':[-a-zA-Z0-9]*:', line):
            b_only_blank = False
        else:
            break
        l += 1
    else:
        l_valid = l

    lines = lines[0:l_valid]

    if lines and not b_only_blank:
        return "\n".join(lines)


#
# Meta
#

def meta(**metadata):
    def d(cls):
        set_meta(cls, metadata)
        return cls
    return d


def set_meta(class_or_instance, key, value=None):
    if not inspect.isclass(class_or_instance):
        class_or_instance = type(class_or_instance)
    
    if not hasattr(class_or_instance, '__meta'):
      setattr(class_or_instance, '__meta', dict())
    
    meta = getattr(class_or_instance, '__meta')

    if isinstance(key, Mapping) and value is None:
      meta.update(key)
    else:
      meta[key] = value


def get_meta(class_or_instance, key=None, default=None):
  if not inspect.isclass(class_or_instance):
      class_or_instance = type(class_or_instance)
  
  if key is None:
      return getattr(class_or_instance, '__meta', {})

  return getattr(class_or_instance, '__meta', {}).get(key, default)


def namespace(name, relative=False, inherit=True):
    def d(cls):

        if relative:
            ns = get_meta(cls, 'namespace', '')
            if ns:
                ns += '/'
            ns += name
        else:
            ns = name

        if not inherit:
            set_meta(cls, 'namespace_parent', get_meta(cls, 'namespace'))

        set_meta(cls, 'namespace', ns)

        update_registered_class(cls)

        return cls

    return d


#
# class
#


def discriminate(key='type', codec=None, **extra):
    if codec is None:
        codec = (get_definition_name, get_registered_class)

    def d(cls):
        set_meta(cls, 'discriminate_key', key)
        set_meta(cls, 'discriminate_codec', codec)
        set_meta(cls, 'discriminate_cls', cls)

        attr(key, type=String(allow_empty=False), mode=READ_ONLY, default=codec[0], **extra)(cls)

        return cls

    return d


def _discriminate_cls(cls, data):
    key = get_meta(cls, 'discriminate_key')
    if key is None:
        return cls
    codec = get_meta(cls, 'discriminate_codec')
    try:
        s = data[key]
    except KeyError:
        base_cls = get_meta(cls, 'discriminate_cls')
        if base_cls is not cls and issubclass(cls, base_cls) and not is_abstract(cls):
            # fall back to the given class
            return cls
        raise Exception('the attribute "%s" is mandatory' % key)
    else:
        _cls = codec[1](s)
        if _cls is None:
            raise Exception('Unable to associate a class to %s' % s)
        return _cls


def abstract(cls):
    set_meta(cls, 'abstract', True)
    return cls


def is_abstract(cls):
    return inspect.isabstract(cls) or get_meta(cls, 'abstract', False)


#
# Attributes
#

READ_ONLY = 2
PRIVATE = 4


# context


class BoundedContext(dict):
  pass


def get_context(obj, context=None):
  if isinstance(context, BoundedContext):
    return context
  else:
    reg = install(obj, True)
    if reg is not None:
      ctx = reg.context
      if context is not None:
        ctx = ctx.copy()
        ctx.update(context)
    else:
      ctx = context
    
    return BoundedContext(ctx) if ctx is not None else BoundedContext()

def set_context(obj, *args, **kwargs):
  install(obj).update_context(*args, **kwargs)


class RegObject(object):
  def __init__(self, obj):
    self.obj = obj
    self._parents = list()
    self._children = list()
    self._dirty = False
    self.data = dict()
    self._context = dict()
    try:
      self.update_context(object.__getattribute__(obj, '__get_context__')())
    except AttributeError:
      pass

  @property
  def context(self):
    return self._context
  
  def update_context(self, key, value=None):
    if isinstance(key, string_types):
      self._context[key] = value
    else:
      self._context.update(key)
  
  @property
  def parents(self):
    return self._parents
  
  @property
  def children(self):
    return self._children
  
  def attach(self, child):
    if child is None or isinstance(child, scalar_types): return
    try:
        install(child)._parents.append(self.obj)
        self._children.append(child)
    except AttributeError:
        return
  
  def detach(self, child):
    reg = install(child, True)
    if reg is None: return
    reg._parents.remove(self.obj)
    self._children.remove(child)

  @property
  def dirty(self):
    return self._dirty
  
  def set_dirty(self, child=None):
    self._dirty = True
    # notify the parent
    for p in self._parents:
      set_dirty(p, child=self.obj)
  
  def clean(self):
    if self._dirty:
      self._dirty = False
      # clean the children
      for c in self.children:
        clean(c)


class RegObjectWithAttr(RegObject):

  def __init__(self, obj):
    super(RegObjectWithAttr, self).__init__(obj)
    self._children = dict()
    self._dirty_attr = set()
  
  @property
  def children(self):
    return self._children.values()
  
  def attach(self, child, attr):
    if child is None or isinstance(child, scalar_types): return
    try:
        install(child)._parents.append(self.obj)
        self._children[attr] = child
    except AttributeError:
        return
  
  def detach(self, child, attr):
    reg = install(child, True)
    if reg is None: return
    reg._parents.remove(self.obj)
    self._children.pop(attr, None)

  def set_dirty(self, child=None, attr=None):
    self._dirty = True
    if child is not None:
      # find the corresponding attributes
      children_map = self._children
      watched = False
      for attr in children_map:
        if children_map[attr] is child:
          self._dirty_attr.add(attr)
          if not watched:
            watched = True # trigger only one time
            attr.__watch__(self.obj, child, child)
    elif attr is not None:
      self._dirty_attr.add(attr)
    
    super(RegObjectWithAttr, self).set_dirty(child=child)
  
  def clean(self):
    self._dirty_attr.clear()
    super(RegObjectWithAttr, self).clean()
  
  def list_dirty_attr(self):
    return self._dirty_attr


scalar_types = string_types + integer_types + (bool, float, text_type, binary_type)


def attach(obj, child):
  install(obj).attach(child)

def detach(obj, child):
  install(obj).detach(child)

def set_dirty(obj, child=None):
  install(obj).set_dirty(child=child)

def is_dirty(obj):
  reg = install(obj, True)
  if reg is None:
    return False
  return reg.dirty

def clean(obj):
  install(obj).clean()


def install(obj, ro=False, cls=None):
  try:
    reg = object.__getattribute__(obj, '__reg__')
  except AttributeError:
    if not ro:
      if cls is None:
        if list_registered_attr(obj):
          cls = RegObjectWithAttr
        else:
          cls = RegObject
      reg = cls(obj)
      object.__setattr__(obj, '__reg__', reg)
    else:
      reg = None
  return reg


def list_dirty_attr(obj):
  res = []
  reg = install(obj, True)
  if reg is not None and isinstance(reg, RegObjectWithAttr):
    res += reg.list_dirty_attr()
  return res


class _NO_VALUE(object):
    pass

NO_VALUE = _NO_VALUE()


class RegItemBase (MutableMapping):
    
    def __init__(self, name, props=None):
        self._name = name
        self._props = dict()
        if props is not None:
            self.update(props)
    
    @property
    def properties (self):
      return self._props
    
    @property
    def name (self):
      return self._name
    
    @property
    def required (self):
      return 'default' not in self

    def update(self, *args, **kwargs):
      props = dict(*args, **kwargs)

      for k in props:
          v = props[k]
          if k == 'type':
            v = convert_type(v)
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

    #used for using this object as dict key
    def __hash__(self):
        return hash(self.name)

    #used for using this object as dict key
    def __eq__(self, other):
      if isinstance(other, RegItemBase):
        return self.name == other.name
      return self.name == other
    
    def make_default(self, *args, **kwargs):
      if 'default' not in self:
        raise AttributeError('%s: no default set' % self._name)
      default_val = self['default']
      if callable(default_val):
        default_val = default_val(*args, **kwargs)
      else:
        default_val = copy.deepcopy(default_val)
      return default_val
    
    def _make_default(self, *args, **kwargs):
      context = kwargs.pop('context', None)
      d = self.make_default(*args, **kwargs)
      data_type = self.get('type')
      if data_type:
        d = data_type.set(d, context=context)
      return d
    
    def toSchema(self, cls, **kwargs):

      data_type = self.get('type')

      if data_type:
        schema = data_type.toSchema(context=kwargs)
      else:
        schema = {}
      
      if 'default' in self:
        try:
          d = self._make_default(cls, context=kwargs)
          if data_type:
            d = data_type.toJson(d, context=kwargs)
          schema['default'] = d
        except Exception as e:
          # todo: print some warning somewhere
          pass

      if 'description' in self and self['description']:
        schema['description'] = self.get('description').strip()

      if self.get('mode') == READ_ONLY:
          schema['$readOnly'] = True

      if 'label' in self and self['label']:
        schema['title'] = self.get('label')
      
      return schema


class Attribute (RegItemBase):
    
    def __init__(self, name, cls=None, props=None):
      super(Attribute, self).__init__(name, props)
      self.cls = cls

    @property
    def cls (self):
      return getattr(self, '_cls', None)

    @cls.setter
    def cls(self, value):
        if value is None:
            return

        if hasattr(self, '_cls'):
            raise Exception('cls attribute already set')
        self._cls = value
        # add the attribute to the class docstring
        if self.get('mode') != PRIVATE:
            docstr = "\n\n.. attribute:: %s\n" % self.name
            description = self.get('description')
            if description:
                docstr += "\n    %s\n" % description
            try:
                value.__doc__ = (value.__doc__ or '') + docstr
            except AttributeError:
                # on python 2 : AttributeError: attribute '__doc__' of 'type' objects is not writable
                pass

    
    def __get_raw__(self, obj, objtype, context=None):
      if obj is None:
        # return default
        val = self._make_default(objtype, context=get_context(obj, context))
      else:
        reg = install(obj, cls=RegObjectWithAttr)
        d = reg.data
        if self._name not in d:
          v = self._make_default(objtype, context=get_context(obj, context))
          reg.attach(v, self)
          d[self._name] = v
        val = d[self._name]
      return val
    
    def __get__(self, obj, objtype=None):
      if objtype is None:
        objtype = type(obj)

      context = get_context(obj)

      val = self.__get_raw__(obj, objtype, context=context)
      return self.__get_post__(val, context)
    
    def __get_post__(self, val, context=None):
      data_type = self.get('type')
      if data_type:
        val = data_type.get(val, context)
      return val
    
    def __get_json__(self, obj, context=None):
      context = get_context(obj, context)
      val = self.__get_raw__(obj, type(obj), context)
      
      data_type = self.get('type')
      if data_type:
        val = data_type.toJson(val, context)
      
      return val
    
    def __set_raw__(self, obj, val, context=None):
      reg = install(obj, cls=RegObjectWithAttr)
      context = get_context(obj, context)
      init = context.get('__init') if context else False

      old_val = reg.data.get(self._name, NO_VALUE)
      reg.detach(old_val, self)
      reg.attach(val, self)
      reg.data[self._name] = val

      if not init:
        # detect change !
        if self.get('force_watch') or not (type(val)==type(old_val) and val==old_val): # val is not old_val:
          #print('__set_raw__', val, old_val, type(val), type(old_val), val is not old_val, val != old_val)
          reg.set_dirty(attr=self)
          self.__watch__(obj, val, old_val, context)
    
    def __watch__(self, obj, val, old_val, context=None):
      try:
        watcher = object.__getattribute__(obj, '__watch__')
      except AttributeError:
        pass
      else:
        reg = install(obj)
        if reg.context.get('__watching'): return
        data_type = self.get('type')
        if data_type:
          # convert the values
          context = get_context(obj, context)
          val = data_type.get(val, context)
          if old_val is NO_VALUE:
            old_val = None
          else:
            old_val = data_type.get(old_val, context)
        reg.context['__watching'] = True
        try:
            watcher(self, val, old_val)
        finally:
            del reg.context['__watching']

    def __set__(self, obj, val):
      context = get_context(obj)
      val = self.__set_pre__(val, context)
      self.__set_raw__(obj, val, context)
    
    def __set_pre__(self, val, context=None):
      data_type = self.get('type')
      if data_type:
        try:
          val = data_type.set(val, context)
        except ValueError as e:
          raise ValueError('%s: %s' % (self._name, str(e)))
      return val

    def __serialize__(self, obj, context=None):
      context = get_context(obj, context)
      val = self.__get_raw__(obj, type(obj), context)

      data_type = self.get('type')
      if data_type:
        val = data_type.serialize(val, context)
      
      return val
    
    def __unserialize__(self, val, context=None):
      data_type = self.get('type')
      if data_type:
        val = data_type.unserialize(val, context)
      return val
    
    def __from_json__(self, val, context=None):
      data_type = self.get('type')
      if data_type:
        val = data_type.fromJson(val, context)
      return val

    def __str__(self):
      return "<attr name=%s cls=%s>" % (self.name, self.cls.__name__ if self.cls else None)
    
    def __repr__(self):
      return str(self)
    
    def clone(self, new_cls):
      copy = type(self)(self.name, new_cls, self._props.copy())
      return copy
      


class ComputedAttr(Attribute):
  
  def __init__(self, func, name=None, cls=None, props=None):
    if name is None:
      if isinstance(func, (staticmethod, classmethod)):
        name = func.__func__.__name__
      else:
        name = func.__name__
    if props is None:
      props = {}
    props.setdefault('mode', READ_ONLY)
    props.setdefault('description', extract_from_docstring(func.__doc__))
    super(ComputedAttr, self).__init__(name, cls, props)
    self._func = func
  
  def __get_raw__(self, obj, objtype, context=None):
      if isinstance(self._func, staticmethod):
        val = self._func.__func__()
      elif isinstance(self._func, classmethod):
        val = self._func.__func__(objtype)
      else:
        if obj is None:
          raise ValueError('no instance')
        else:
          val = self._func(obj)
      return val
  
  def __set_raw__(self, obj, val, context=None):
      raise ValueError('[%s] computed attributes are read only' % self._name)

  def clone(self, new_cls):
      copy = type(self)(self._func, self.name, new_cls, self._props.copy())
      return copy


def attr(name=None, **kwargs):
  def d(item):

    if inspect.isclass(item):
      cls = item

      if name is None:
        raise Exception('name argument is mandatory')

      attributes = list_registered_attr(cls)

      for i in range(len(attributes)):
        a = attributes[i]
        if a.name == name:
          if a.cls == cls:
            a.update(kwargs)
            attribute = a
          else:
            # come from a base class, copy it before updating
            attribute = a.clone(cls)
            attribute.update(kwargs)
            setattr(cls, name, attribute)
          break
      else:
        attribute = Attribute(name, cls, props=kwargs)
        setattr(cls, name, attribute)

      return cls

    else:
      # computed attribute
      func = item
      return ComputedAttr(func, name=name, props=kwargs)
  return d


default_alphabet = string.ascii_letters + string.digits

def randomString(length=7, alphabet=default_alphabet):
    """Generate a random string """
    return ''.join(random.choice(alphabet) for i in range(length))


def uid(key='id', generator=None, **extra):
  if generator is None:
    generator = randomString
  
  def d(cls):
    attr(key, type=String(allow_empty=False), mode=READ_ONLY, default=lambda _: generator(), **extra)(cls)
    return cls
  return d


def list_registered_attr(class_or_instance):
  """
  list the attributes of the given class or instance.
  """
  if inspect.isclass(class_or_instance):
    cls_dict = class_or_instance.__dict__
  else:
    cls_dict = type(class_or_instance).__dict__.copy()
    cls_dict.update(getattr(class_or_instance, '__dict__', {}))
  
  attributes = []
  for name in cls_dict:
    attr = cls_dict[name]
    if isinstance(attr, Attribute):
      attributes.append(attr)
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

    signals = get_meta(cls, 'signals', [])

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
    
    set_meta(cls, 'signals', signals)

    return cls
  return d

def list_registered_signals(class_or_instance):
  """
  list the signals the given class or instance may throw.
  """
  return get_meta(class_or_instance, 'signals', [])


#
# Methods
#


class MethodDecorator(object):

    def __call__(self, func):
      return self._init(func)

    def _init(self, func):
        """
        set the default metadata
        """
        if not isinstance(func, Method):
          func = Method(func)
        return func

    # decorators

    def name(self, name):
        def d(func):
            func = self._init(func)
            func.properties['name'] = name
            return func
        return d

    def description(self, description):
        def d(func):
            func = self._init(func)
            func.properties['description'] = description
            return func
        return d

    def return_type(self, return_type):
        def d(func):
            func = self._init(func)
            if isinstance(return_type, string_types) and re.search('^[^/]+/[^/]+$', return_type):
                # mime type
                func.properties['return_type'] = return_type
            else:
                func.properties['return_type'] = convert_type(return_type)
            return func
        return d

    def arg(self, name, **kwargs):
        def d(func):
            func = self._init(func)
            args = func.properties['args']
            
            if not kwargs.get('enable', True):
                args.pop(name, None)
            else:
                if name not in args:
                  args[name] = Argument(name, kwargs)
                else:
                  args[name].update(kwargs)

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


class Argument(RegItemBase):
  pass


class Method(RegItemBase):

    def __init__(self, func, name=None):
      if name is None:
        if hasattr(func, '__name__'):
          name = getattr(func, '__name__')
        else:
          name = getattr(func, '__func__').__name__
      
      super(Method, self).__init__(name, props=self._parse(func))
      self._func = func
      self._cls = None
    
    @property
    def cls (self):
      return self._cls
    
    @property
    def func (self):
      return self._func
    
    def __str__(self):
      return "<method name=%s cls=%s>" % (self.name, self.cls.__name__ if self.cls else None)
    
    def __repr__(self):
      return str(self)
    
    def __get__(self, obj, objtype=None):
      def handler(*args, **kwargs):
        _kwargs = self._parse_args(args, kwargs, context=get_context(obj))
        return self._func.__get__(obj, objtype)(**_kwargs)
      return handler

    def call(self, obj, *args, **kwargs):
        return self.__get__(obj)(*args, **kwargs)
    
    def _parse_args(self, args, kwargs, context=None):
      _args = self.get('args')
      arg_dict = OrderedDict()
      _args_list = list(_args)

      for argi in range(len(args)):
        if argi >= len(_args_list):
          raise ValueError("%s() takes at most %d arguments" % (self.name, len(_args_list)))
        arg_name = _args_list[argi]
        arg_dict[arg_name] = args[argi]
      
      for arg_name in kwargs:
        if arg_name not in _args_list:
            raise ValueError("%s(): invalid argument '%s'" % (self.name, arg_name))
        if arg_name in arg_dict:
          raise ValueError("%s(): got multiple values for keyword argument '%s'" % (self.name, arg_name))
        arg_dict[arg_name] = kwargs[arg_name]

      # check the arguments
      for arg_name in arg_dict:
        arg = _args[arg_name]
        arg_type = arg.get('type')
        if arg_type:
          try:
            arg_dict[arg_name] = arg_type.set(arg_dict[arg_name], context)
          except Exception as e:
            raise ValueError("%s(): argument '%s' is invalid: %s" % (self.name, arg_name, str(e)))

      # check missing argument !
      for arg_name in _args:
        arg = _args[arg_name]
        if arg_name not in arg_dict:
          if 'default' in arg:
            arg_dict[arg_name] = arg.make_default()
          else:
            if arg.get('required', False):
              raise ValueError("%s(): missing argument '%s'" % (self.name, arg_name))
      
      return arg_dict

    def toSchema(self, **kwargs):
        schema = {
            'type': 'function'
        }

        args_dict = self.get('args')

        required = []
        arguments = OrderedDict()
        for arg_name in args_dict:
            arg = args_dict[arg_name]

            if ('default' not in arg) or arg.get('required', False):
                required.append(arg_name)

            arg_type = arg.get('type')

            if arg_type:
              arg_schema = arg_type.toSchema(context=kwargs)
            else:
              arg_schema = {}

            if 'description' in arg:
              arg_schema['description'] = arg.get('description').strip()

            if 'default' in arg:
              try:
                default_value = arg._make_default(context=kwargs)
                if arg_type:
                  default_value = arg_type.toJson(default_value, context=kwargs)
                arg_schema['default'] = default_value
              except Exception:
                # todo: warn somehow
                pass

            arguments[arg_name] = arg_schema

        schema['required'] = required
        schema['arguments'] = arguments

        if 'description' in self:
          schema['description'] = self.get('description')

        return_type = self.get('return_type')
        if isinstance(return_type, Type):
            schema['return'] = return_type.toSchema(context=kwargs)
        else:
            schema['return'] = return_type

        return schema
  
    @staticmethod
    def inherit(func, orig):
      """
      makes func defaults from orig (no overwritting)
      """
      func = method._init(func)
      _setdefaults(func.properties, orig.properties)
      return func
    
    @staticmethod
    def _parse(func):
        """
        extract some metadata from a method
        """
        if hasattr(func, '__func__'):
          func = getattr(func, '__func__')

        name = func.__name__
        description = extract_from_docstring(func.__doc__) or ''

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
                continue

            if arg_name == "args" or arg_name == "kwargs":
                raise Exception('not compatible with args or kwargs arguments !') # todo

            has_default = (i >= default_offset)

            arg_meta = {}

            if has_default:
              default = var_defaults[i - default_offset] if has_default else None
              arg_meta['default'] = default
              arg_meta['type'] = get_type_from_value(default)
            
            meta['args'][arg_name] = Argument(arg_name, arg_meta)

        if description:
            meta['description'] = description

        meta['name'] = name
        meta['func_name'] = name

        return meta


def list_registered_methods(class_or_instance):
  """
  list the methods of the given class or instance.
  """
  if not inspect.isclass(class_or_instance):
    class_or_instance = type(class_or_instance)

  methods = []
  for name, value in getmembers(class_or_instance, lambda x: isinstance(x, Method)):
    methods.append(value)
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
    return is_meta_class(cls) and registered_cls.get(get_definition_name(cls)) is cls

def get_registered_class(name):
    if name not in registered_cls:
        raise Exception('No registered class: "%s"' % (name))
    return registered_cls[name]

def register_class(cls):
    cls_name = get_definition_name(cls)
    if cls_name in registered_cls:
        raise Exception('A class with the name "%s" already exists: %s' % (cls_name, registered_cls.get(cls_name)))

    registered_cls[cls_name] = cls

def update_registered_class(cls):
    cls_name = get_definition_name(cls)
    if cls_name not in registered_cls:
        for n in list(registered_cls):
            c = registered_cls.get(n)
            if cls is c:
                del registered_cls[n]
                registered_cls[cls_name] = cls


class MetaReg(ABCMeta):

    """MetaReg metaclass"""

    def __new__(meta, name, bases, dct):
      cls = ABCMeta.__new__(meta, name, bases, dct)

      inherited_meta = get_meta(cls).copy()

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
            c = attribute.clone(cls)
            c.update(attribute_b.properties)
            extended_attributes[i] = c

      for a in extended_attributes:
        setattr(cls, a.name, a)

      # look for computed attributes
      for name in dct:
          member = dct.get(name)
          if isinstance(member, ComputedAttr):
            if member.cls is None:
              member.cls = cls

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

      inherited_meta.update({
          'signals': extended_signals,
          'abstract': False,
          'description': extract_from_docstring(cls.__doc__),
          'label': format_label(cls.__name__)
      })

      if 'namespace_parent' in inherited_meta:
          inherited_meta['namespace'] = inherited_meta['namespace_parent']
          del inherited_meta['namespace_parent']

      setattr(cls, '__meta', inherited_meta)

      # methods

      for m in list_registered_methods(cls):
        if m.cls is None:
          m._cls = cls

      for base in bases:
        for b_m in list_registered_methods(base):

          if b_m.name in cls.__dict__:
            member = cls.__dict__[b_m.name]

            if member is b_m:
              continue # inherited from parent, no modification done
            
            # overloading
            member = Method.inherit(member, b_m)
            setattr(cls, b_m.name, member)

      # globals
      if getattr(cls, '_REGISTER_', True):
        register_class(cls)

      return cls


def get_definition_name(cls):
  """
  returns the definition name for the given class or instance (e.g. "#/resources/Resource")
  """
  name = cls.__name__
  ns = get_meta(cls, 'namespace')
  if ns:
      return '%s/%s' % (ns, name)
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
          '$ref': '#/' + get_definition_name(cls)
      }

  attributes = list_registered_attr(cls)

  schema = {
      "type": "class",
      "properties": OrderedDict(),
      "additionalProperties": False,
      "title": get_meta(cls, 'label')
  }

  icon = get_meta(cls, 'icon')
  if icon:
      schema['icon'] = icon

  color = get_meta(cls, 'color')
  if color:
      schema['color'] = color

  category = get_meta(cls, 'category')
  if category:
      schema['category'] = category

  required = []

  description = get_meta(cls, 'description') or ''
  description = description.strip()
  if description:
    schema['description'] = description

  if not no_signals:
      signals = []
      for signal_ in list_registered_signals(cls):
          if (not flatted) and cls is not signal_.cls:
              continue
          signals.append(get_definition_name(signal_.signal))
      if len(signals) > 0:
          schema['signals'] = signals

  for attribute in attributes:
    mode = attribute.get('mode')
    name = attribute.name

    if (not flatted) and cls is not attribute.cls:
      continue

    if mode == PRIVATE:
      continue

    attr_schema = attribute.toSchema(cls, **kwargs)

    if mode != READ_ONLY:
        if 'default' not in attr_schema:
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

  if hasattr(cls, '__schema__'):
      schema = cls.__schema__(schema, context=kwargs)

  if not flatted:
    all_of = []

    for b in cls.__bases__:
      if subclass is not None and not issubclass(b, subclass):
          continue
      if b in skip:
          continue
      if is_registered_class(b):
        all_of.append({
          '$ref': '#/' + get_definition_name(b)
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

  subclass = kwargs.get('subclass')
  skip = kwargs.get('skip') or ()

  kwargs.update({
    'flatted': False,
    'root': True
  })

  for cls in list_registered_classes():

    if subclass is not None and not issubclass(cls, subclass):
        continue

    if cls in skip:
        continue

    ns = get_meta(cls, 'namespace')

    schema = build_schema(cls, **kwargs)

    rel_def = definitions
    if ns:
      for ns_item in ns.split('/'):
        if ns_item not in rel_def:
          rel_def[ns_item] = OrderedDict()
        rel_def = rel_def[ns_item]
    
    rel_def[cls.__name__] = schema
  
  return definitions


class InternalData(Mapping):

  def __init__(self, d, context=None):
    self.__d = d
    self.__context = context
    self.__applied = False
  
  def set_to(self, obj):
    if not self.__applied:
      for attr in self.__d:
        data = self.__d[attr]
        attr.__set_raw__(obj, data)
      self.__applied = True

  def __iter__(self):
    return iter([attr.name for attr in self.__d])

  def __len__(self):
    return len(self.__d)

  def __getitem__(self, key):
    for attr in self.__d:
      if attr.name == key:
        data = self.__d[attr]
        return attr.__get_post__(data, self.__context)
    raise KeyError('invalid key: %s' % key)


def _set_base(cls, data=None, context=None, init=False):
  if isinstance(data, InternalData): return data
  d = {}
  for attribute in list_registered_attr(cls):
    if not isinstance(attribute, ComputedAttr):
      name = attribute.name
      if name in data:
        d[attribute] = attribute.__set_pre__(data[name], context)
      elif attribute.required and init:
        raise AttributeError('[%s] attribute "%s" is not set' % (cls.__name__, name))

  return InternalData(d, context)


def _set_json(cls, data=None, context=None, init=False):
    d = {}
    for attribute in list_registered_attr(cls):
        if not isinstance(attribute, ComputedAttr):
            name = attribute.name
            if name in data:
                mode = attribute.get('mode')
                if mode == PRIVATE or (not init and mode == READ_ONLY):
                    raise AttributeError('attribute "%s" is not writable' % name)
                d[attribute] = attribute.__from_json__(data[name], context)

    return InternalData(d, context)


def _set_db(cls, data=None, context=None, init=False):
    d = {}
    for attribute in list_registered_attr(cls):
        if not isinstance(attribute, ComputedAttr):
            name = attribute.name
            model_key = attribute.get('model_key', name)
            if model_key in data:
                d[attribute] = attribute.__unserialize__(data[model_key], context)

    return InternalData(d, context)


def _set(cls, data=None, context=None, init=False, data_src=None):
    if data_src == 'db':
        h = _set_db
    elif data_src == 'json':
        h = _set_json
    else:
        h = _set_base

    return h(cls, data, context, init)


def create(cls, data=None, context=None, data_src=None):
  if isinstance(cls, string_types):
    cls = get_registered_class(cls)

  cls = _discriminate_cls(cls, data)

  if data is None:
    data = {}
  
  d = _set(cls, data, context, True, data_src)

  if hasattr(cls, '__instantiate__'):
    instance = cls.__instantiate__(d, context)
  else:
    instance = cls()
  
  if context is not None:
    set_context(instance, context)

  d.set_to(instance)

  return instance


def update(obj, data, data_src=None):
  cls = type(obj)
  context = get_context(obj)

  d = _set(cls, data, context, False, data_src)
  d.set_to(obj)

  return obj


def init(obj, data, data_src=None):
  cls = type(obj)
  context = get_context(obj)

  d = _set(cls, data, context, True, data_src)

  set_context(obj, '__init', True)
  try:
    d.set_to(obj)
  finally:
    set_context(obj, '__init', False)

  return obj


def serialize(obj, context=None):
  j = {}
  for attribute in list_registered_attr(obj):
    if not isinstance(attribute, ComputedAttr):
        name = attribute.name
        model_key = attribute.get('model_key', name)
        j[model_key] = attribute.__serialize__(obj, context)
  return j


def unserialize(cls, data=None, context=None):
  return create(cls, data, context, data_src='db')


def toJson(obj, context=None):
  j = {}
  for attribute in list_registered_attr(obj):
    if attribute.get('mode') == PRIVATE:
      continue
    name = attribute.name
    j[name] = attribute.__get_json__(obj, context)

  if hasattr(obj, '__json__'):
    j = obj.__json__(j, context=context)

  return j


def fromJson(cls, data, context=None):
  return create(cls, data, context, data_src='json')


registered_types = []


class TypeMetaclass(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        registered_types.append(cls)
        return cls


class Type (with_metaclass(TypeMetaclass, object)):
  
  def __init__(self, **attributes):
    self._attributes = attributes
  
  def __getattr__(self, name):
    return self._attributes.get(name)
  
  def set(self, value, context = None):
    return value

  def get(self, value, context = None):
    return value
  
  def toJson(self, value, context = None):
    return value
  
  def fromJson(self, value, context = None):
    return value
  
  def serialize(self, value, context = None):
    return value
  
  def unserialize(self, value, context = None):
    return value
  
  def toSchema(self, context = None):
    s = {}
    for prop in self._attributes:
      s[prop] = self._attributes[prop]
    return s


class Class(Type):

  def __init__(self, cls, **attributes):
    super(Class, self).__init__(**attributes)
    self.cls = cls
  
  def set(self, value, context = None):
    if not isinstance(value, self.cls):
      raise ValueError('%s not an instance of %s' % (value, self.cls.__name__))
    return value
  
  def unserialize(self, data, context = None):
    return unserialize(self.cls, data, context)
  
  def serialize(self, value, context = None):
    return serialize(value, context)

  def fromJson(self, data, context = None):
    return fromJson(self.cls, data, context)

  def toJson(self, value, context = None):
    return toJson(value, context)
  
  def toSchema(self, context = None):
    if context is None:
      context = {}
    return build_schema(self.cls, **context)


_none_type_class = type(None)


def convert_type(t):
  """
  converts the givent argument to the right type
  """

  if isinstance(t, Type):
    return t
  
  for regtype in registered_types:
    if hasattr(regtype, '__synonyms__'):
      if t in regtype.__synonyms__:
        return regtype()
  
  if inspect.isclass(t):
    return Class(t)

  for regtype in registered_types:
    if hasattr(regtype, '__convert__'):
      try:
        res = regtype.__convert__(t)
        if res is not None:
          return res
      except:
        pass
  
  raise Exception('unknown type "%s"' % str(t))


def get_type_from_value(value):

  for regtype in registered_types:
    if hasattr(regtype, '__convert_value__'):
      try:
        res = regtype.__convert_value__(value)
        if res is not None:
          return res
      except:
        pass

  v_type = type(value)

  return convert_type(v_type)


class Entity(with_metaclass(MetaReg, object)):

    def __init__(self, value=None, context=None, data_src=None):
        if value is None:
            value = {}
        
        install(self)

        if context is not None:
          self.__reg__.update_context(context)
        
        init(self, value, data_src=data_src)
        
        # call parent constructor
        super(Entity, self).__init__()

    @classmethod
    def __instantiate__(cls, data, context):
      return cls(data, context)
    
    def __getattr__( self, name):
      context = self.__reg__.context
      if name in context:
        return context[name]
      raise AttributeError('object %s has no attribute %s' % (self, name))

    def __transaction_start__(self):
        pass

    def __transaction_end__(self):
        pass

    def __watch__(self, attribute, val, old_val):
        #  print('%s.%s changed %s -> %s' % (type(self).__name__, attribute.name, old_val, val))
        t = self.__reg__.context.get('__transaction', 0)
        if t == 0:
            self.__transaction_start__()
            self.__transaction_end__()

    def __enter__(self):
        t = self.__reg__.context.get('__transaction', 0)
        if t==0:
            self.__transaction_start__()
        self.__reg__.context['__transaction'] = t + 1
        return self

    def __exit__(self, type, value, traceback):
        t = self.__reg__.context['__transaction']
        t = t - 1
        try:
            if t == 0: self.__transaction_end__()
        finally:
            self.__reg__.context['__transaction'] = t


def dbg_attr(obj):
    for a in list_registered_attr(obj):
        print(a)


def dbg_tree(obj, prefix=''):
    reg = install(obj, True)
    if reg is None:
        print(prefix + str(obj))
        return

    print('%s%s: dirty:%s' % (prefix, str(obj), reg.dirty))

    for child in reg.children:
        dbg_tree(child, prefix + '  ')


def dbg_data(obj):
    reg = install(obj, True)
    if reg is None:
        return

    data = reg.data
    for k in data:
        print("%s:" % k, data[k])


def dbg(obj):
    print('---------------debug----------------')
    print(obj)
    print('-------------attributes-------------')
    dbg_attr(obj)
    print('---------------tree-----------------')
    dbg_tree(obj)
    print('---------------data-----------------')
    dbg_data(obj)
    print('------------------------------------')



# import types
from .type import *
