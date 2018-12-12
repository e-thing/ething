# coding: utf-8
from .entity import *


class DbEntity(Entity):
    def __init__(self, value=None, create=True, context=None):

        Entity.__init__(self, value, context)

        object.__setattr__(self, '_DbEntity__new', create)
        object.__setattr__(self, '_DbEntity__no_save', 0)
        object.__setattr__(self, '_DbEntity__watch_data', dict())
        object.__setattr__(self, '_DbEntity__destroyed', False)

        self._watch_init()

    def __setattr__(self, name, value):
        super(DbEntity, self).__setattr__(name, value)
        self.save()

    @classmethod
    def create(cls, attributes, context=None):
        instance = cls(attributes, create=True, context=context)
        instance.save()
        return instance

    @classmethod
    def unserialize(cls, data, context = None):
        return super(DbEntity, cls).unserialize(data, context, kwargs={'create': False})

    def save(self):
        with self._lock:
            if self.__no_save > 0:
                return

            if self.__destroyed:
                # raise Exception('resource destroyed: %s' % self)
                return # detroyed, ignore any change !

            if not self.__new and not self._is_dirty():
                return  # nothing to save

            # avoid infinit loop, if save() is called in _insert or _save
            object.__setattr__(self, '_DbEntity__no_save', 1)

            try:

                if self.__new:

                    self._before_insert()

                    self._insert()

                    object.__setattr__(self, '_DbEntity__new', False)

                else:

                    self._before_save()

                    dirty_attrs = self._get_dirty_attrs()

                    for a in dirty_attrs:
                        if a.get('watch'):
                            old_value = self.__watch_data.get(a.name)
                            new_value = self._get(a)
                            self._watch(a.name, new_value, old_value)

                    self._save(dirty_attrs)

                    self._watch_init()

                self._clean()
            except:
                raise
            finally:
                object.__setattr__(self, '_DbEntity__no_save', 0)



    def _watch(self, attr, new_value, old_value):
        pass

    def remove(self):
        with self._lock:
            self._remove()
            object.__setattr__(self, '_DbEntity__new', True)
            object.__setattr__(self, '_DbEntity__destroyed', True)

    def _before_insert(self):
        pass

    def _insert(self):
        raise NotImplementedError()

    def _before_save(self):
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
            if a.get('watch'):
                self.__watch_data[a.name] = self._get(a)

    def export_instance(self):
        return self.serialize()

    @classmethod
    def import_instance(cls, data, context = None):
        instance = super(DbEntity, cls).unserialize(data, context, kwargs={'create': True})
        instance.save()
        return instance
        #return cls.create(data, context)

    @classmethod
    def upgrade(cls, data, version):
        pass