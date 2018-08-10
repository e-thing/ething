# coding: utf-8
from entity import *
import threading


class DbEntity(Entity):
    def __init__(self, value=None, create=True):

        Entity.__init__(self, value)

        object.__setattr__(self, '_DbEntity__new', create)
        object.__setattr__(self, '_DbEntity__no_save', 0)
        object.__setattr__(self, '_DbEntity__watch_data', dict())

        self._watch_init()#

    def __setattr__(self, name, value):
        super(DbEntity, self).__setattr__(name, value)
        self.save()

    @classmethod
    def create(cls, attributes, **ctor_attr):
        instance = cls(attributes, True, **ctor_attr)
        instance.save()
        return instance

    @classmethod
    def unserialize(cls, data, **kwargs):
        return super(DbEntity, cls).unserialize(data, create = False, **kwargs)

    def save(self):
        with self._lock:
            if self.__no_save > 0:
                return

            if not self.__new and not self._is_dirty():
                return  # nothing to save

            # avoid infinit loop, if save() is called in _insert or _save
            object.__setattr__(self, '_DbEntity__no_save', 1)

            try:

                if self.__new:

                    self._insert()

                    object.__setattr__(self, '_DbEntity__new', False)

                else:

                    self._before_save()

                    dirty_attrs = self._get_dirty_attrs()

                    for a in dirty_attrs:
                        on_change = a.get('on_change')
                        if on_change:
                            old_value = self.__watch_data.get(a.name)
                            new_value = self._get(a)
                            on_change(self, new_value, old_value)

                    self._save(dirty_attrs)

                    self._watch_init()

                self._clean()
            except:
                raise
            finally:
                object.__setattr__(self, '_DbEntity__no_save', 0)



#    def refresh(self, keepDirtyFields=False):
#        with self._lock:
#            serialized_data = self._refresh()
#            if not serialized_data: return # nothing to refresh
#            dirty_attrs = set()
#
#            if keepDirtyFields:
#                dirty_attrs = self._get_dirty_attrs()
#
#            for attribute in list_registered_attr(self):
#                name = attribute.name
#                model_key = attribute.get('model_key', name)
#                if model_key in serialized_data:
#                    if keepDirtyFields and attribute in dirty_attrs:
#                        continue
#                    data_type = attribute['type']
#                    self._set(data_type.unserialize(serialized_data.get(model_key)))
#
#            if not keepDirtyFields:
#                self._clean()
#
#            self._watch_init()

    def remove(self):
        with self._lock:
            self._remove()
            object.__setattr__(self, '_DbEntity__new', True)

    def _insert(self):
        raise NotImplementedError()

    def _before_save(selfself):
        pass

    def _save(self, dirty_attrs):
        raise NotImplementedError()

    #def _refresh(self):
    #    raise NotImplementedError()

    def _remove(self):
        raise NotImplementedError()

    def __enter__(self):
        self._lock.acquire()
        # necessary to take into account nested with statements
        object.__setattr__(self, '_DbEntity__no_save', self.__no_save + 1)
        return self

    def __exit__(self, type, value, traceback):
        # necessary to take into account nested with statements
        object.__setattr__(self, '_DbEntity__no_save', self.__no_save - 1)
        self.save()
        self._lock.release()

    def _watch_init(self):
        self.__watch_data.clear()
        for a in list_registered_attr(self):
            if a.get('on_change'):
                self.__watch_data[a.name] = self._get(a)
