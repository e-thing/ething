# coding: utf-8
from future.utils import with_metaclass
from .reg import *
import threading


default_type = Basetype()


class Entity(with_metaclass(MetaReg, M_Class)):

    @staticmethod
    def _attr_modifier_ (attribute):
      attribute.setdefault('type', default_type)
      attribute['type'] = convert_type(attribute['type'])
      attribute.setdefault('model_key', attribute.name)
    

    def __init__(self, value = None, context = None):

        if is_abstract(self):
            raise Exception('Unable to create a new instance of the abstract class %s' % type(self).__name__)

        if value is None:
            value = {}

        M_Class.__init__(self)

        attributes = list_registered_attr(self)

        # make some private fields
        object.__setattr__(self, '_Entity__d', {})
        object.__setattr__(self, '_Entity__attributes', attributes)
        object.__setattr__(self, '_Entity__dirty_attrs', set())
        object.__setattr__(self, '_lock', threading.RLock())
        object.__setattr__(self, '_context', context)

        for attribute in attributes:
            if attribute.get('compute') is None:
                name = attribute.name
                if name in value:
                  self._set(attribute, value[name])
                elif 'default' in attribute:
                  self._set(attribute, attribute.make_default(self.__class__))
                else:
                  raise AttributeError('attribute "%s" is not set' % name)

    def _getattr(self, name):
      for a in self.__attributes:
        if a.name == name:
          return a

    def __getattr__(self, name):
        #with self._lock:
        attribute = self._getattr(name)

        if attribute is None:
            raise AttributeError('no attribute "%s"' % name)

        return self._get(attribute)

    def _get_raw(self, attribute):
        compute = attribute.get('compute')
        if compute is not None:
            value = compute(self)
        else:
            name = attribute.name
            value = self.__d[name]
        return value

    def _get(self, attribute):
        data_type = attribute['type']
        return data_type.get(self._get_raw(attribute), self._context)

    def __setattr__(self, name, value):
        with self._lock:

            attribute = self._getattr(name)

            if attribute is None:
                raise AttributeError('no attribute "%s"' % name)

            self._set(attribute, value)

            self._set_dirty(attribute)
    
    def _set(self, attribute, value):
        name = attribute.name
        if attribute.get('compute') is not None:
            raise Exception('unable to set a computed attribute "%s"' % name)
        data_type = attribute['type']
        value = data_type.set(value, self._context)
        self.__d[name] = value
        return value
    
    def toJson(self, context = None):
      #with self._lock:
      j = {}
      for attribute in self.__attributes:
        name = attribute.name

        if attribute.get('mode') == PRIVATE:
          continue

        data_type = attribute['type']
        j[name] = data_type.toJson(self._get_raw(attribute), merge_context(self._context, context))
      return j
    
    def serialize(self, context = None):
        with self._lock:
          j = {}
          for attribute in self.__attributes:
            if attribute.get('compute') is None:
                name = attribute.name
                model_key = attribute.get('model_key', name)
                data_type = attribute['type']
                j[model_key] = data_type.serialize(self.__d[name], merge_context(self._context, context))
          return j
    
    def _children(self):
      return [ item for item in self.__d.values() if isinstance(item, Memory) ]
    
    def _clean(self):
      self.__dirty_attrs.clear()
      M_Class._clean(self)
    
    def _set_dirty(self, attribute):
      self.__dirty_attrs.add(attribute)
      M_Class._set_dirty(self)
    
    def _get_dirty_attrs(self):
        dirty_attrs = set(self.__dirty_attrs)

        for a in self.__attributes:
            if a not in dirty_attrs:
                item = self.__d.get(a.name)
                if isinstance(item, Memory):
                    if item._is_dirty():
                        dirty_attrs.add(a)

        return dirty_attrs
    
    def updateFromJson(self, data, context = None):
        with self._lock:
          for key in data:
            attribute = self._getattr(key)
            if attribute:
              name = attribute.name
              mode = attribute.get('mode')
              if mode == PRIVATE or mode == READ_ONLY:
                  continue
              data_type = attribute.get('type')

              old_value = self._get(attribute)
              new_value = self._set(attribute, data_type.fromJson(data[name], merge_context(self._context, context)))

              if isinstance(new_value, Memory) or old_value != new_value:
                  self._set_dirty(attribute)
    
    @classmethod
    def unserialize(cls, data, context = None, kwargs = None):
      j = {}
      for attribute in list_registered_attr(cls):
          if attribute.get('compute') is None:
            name = attribute.name
            data_type = attribute['type']
            model_key = attribute.get('model_key', name)
            if model_key in data:
                j[name] = data_type.unserialize(data.get(model_key), context)
      if kwargs is None:
          kwargs = {}
      return cls(j, context=context, **kwargs)
    
    @classmethod
    def fromJson(cls, data, context = None, kwargs = None):
      j = {}
      for attribute in list_registered_attr(cls):
          if attribute.get('compute') is None:
            name = attribute.name
            if name in data:
              mode = attribute.get('mode')
              if mode == PRIVATE:
                raise AttributeError('attribute "%s" is not writable' % name)
              data_type = attribute['type']
              if name in data:
                j[name] = data_type.fromJson(data.get(name), context)
      if kwargs is None:
          kwargs = {}
      return cls(j, context=context, **kwargs)
    
    @classmethod
    def toSchema(cls, context = None):
      if context is None:
          context = {}
      return build_schema(cls, **context)
      



