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
    

    def __init__(self, value = {}, **kwargs):

        if is_abstract(self):
            raise Exception('Unable to create a new instance of the abstract class %s' % type(self).__name__)

        M_Class.__init__(self)

        attributes = list_registered_attr(self)

        # make some private fields
        object.__setattr__(self, '_Entity__d', {})
        object.__setattr__(self, '_Entity__attributes', attributes)
        object.__setattr__(self, '_Entity__dirty_attrs', set())
        object.__setattr__(self, '_lock', threading.RLock())

        for attribute in attributes:
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
        with self._lock:
            priv_access = False

            if name.startswith('_'):
                priv_access = True
                name = name[1:]

            attribute = self._getattr(name)

            if attribute is None:
                raise AttributeError('no attribute "%s"' % name)

            if attribute.get('mode') == PRIVATE and not priv_access:
                raise AttributeError('attribute "%s" is not readable' % name)

            return self._get(attribute)

    def _get(self, attribute):
        name = attribute.name
        value = self.__d[name]
        data_type = attribute['type']
        return data_type.get(value, self)

    def __setattr__(self, name, value):
        with self._lock:
            priv_access = False

            if name.startswith('_'):
                priv_access = True
                name = name[1:]

            attribute = self._getattr(name)

            if attribute is None:
                raise AttributeError('no attribute "%s"' % name)

            mode = attribute.get('mode')
            if (mode == PRIVATE or mode == READ_ONLY) and not priv_access:
                raise AttributeError('attribute "%s" is not writable' % name)

            self._set(attribute, value)

            self._set_dirty(attribute)
    
    def _set(self, attribute, value):
        name = attribute.name
        data_type = attribute['type']
        value = data_type.set(value, self)
        self.__d[name] = value
        return value
    
    def toJson(self, **kwargs):
        with self._lock:
          j = {}
          for attribute in self.__attributes:
            name = attribute.name

            if attribute.get('mode') == PRIVATE:
              continue

            data_type = attribute['type']
            j[name] = data_type.toJson(self.__d[name], **kwargs)
          return j
    
    def serialize(self, **kwargs):
        with self._lock:
          j = {}
          for attribute in self.__attributes:
            name = attribute.name
            model_key = attribute.get('model_key', name)
            data_type = attribute['type']
            j[model_key] = data_type.serialize(self.__d[name], **kwargs)
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
                item = self.__d[a.name]
                if isinstance(item, Memory):
                    if item._is_dirty():
                        dirty_attrs.add(a)

        return dirty_attrs
    
    def updateFromJson(self, data, **kwargs):
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
              new_value = self._set(attribute, data_type.fromJson(data[name], **kwargs))

              if isinstance(new_value, Memory) or old_value != new_value:
                  self._set_dirty(attribute)
    
    @classmethod
    def unserialize(cls, data, **kwargs):
      j = {}
      for attribute in list_registered_attr(cls):
        name = attribute.name
        data_type = attribute['type']
        model_key = attribute.get('model_key', name)
        if model_key in data:
            j[name] = data_type.unserialize(data.get(model_key), **kwargs)
      return cls(j, **kwargs)
    
    @classmethod
    def fromJson(cls, data, **kwargs):
      j = {}
      for attribute in list_registered_attr(cls):
        name = attribute.name
        if name in data:
          mode = attribute.get('mode')
          if mode == PRIVATE:
            raise AttributeError('attribute "%s" is not writable' % name)
          data_type = attribute['type']
          if name in data:
            j[name] = data_type.fromJson(data.get(name), **kwargs)
      return cls(j, **kwargs)
    
    @classmethod
    def toSchema(cls, **kwargs):
      return build_schema(cls, **kwargs)
      



