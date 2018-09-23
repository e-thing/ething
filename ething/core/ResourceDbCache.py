# coding: utf-8

from .reg import get_registered_class
import logging
import threading
from future.utils import string_types
import re


class LogLock(object):
    def __init__(self, name, lock, logger):
        self.name = str(name)
        self.lock = lock
        self.logger = logger

    def acquire(self, blocking=True):
        thread = threading.current_thread()
        self.logger.debug("{0:x} Trying to acquire {1} lock from thread {2}:{3}".format(
            id(self), self.name, thread.name, thread.ident))
        ret = self.lock.acquire(blocking)
        if ret == True:
            self.logger.debug("{0:x} Acquired {1} lock from thread {2}:{3}".format(
                id(self), self.name, thread.name, thread.ident))
        else:
            self.logger.debug("{0:x} Non-blocking aquire of {1} lock failed from thread {2}:{3}".format(
                id(self), self.name, thread.name, thread.ident))
        return ret

    def release(self):
        thread = threading.current_thread()
        self.logger.debug("{0:x} Releasing {1} lock from thread {2}:{3}".format(id(self), self.name, thread.name, thread.ident))
        self.lock.release()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False    # Do not swallow exceptions


class ResourceDbCache(object):

    def __init__ (self, core):
        self.__core = core
        self.__db = core.db
        self.__resources = dict()
        self.__log = logging.getLogger("ething.ResourceDbCache")
        self.__lock = threading.RLock() # LogLock('ResourceDbCache', threading.RLock(), self.__log)

        self._load()

    def _load(self):
        with self.__lock:

            self.__resources.clear()

            cnt = 0

            for doc in self.__db.list_resources():
                cl = get_registered_class(doc['type'])
                if cl is not None:
                    try:
                        instance = cl.unserialize(doc, ething=self.__core)

                        self.__resources[instance.id] = instance

                        cnt += 1

                    except:
                        self.__log.exception('error loading resource: name=%s type=%s id=%s' % (
                            doc.get('name'), doc.get('type'), doc.get('id')))

            self.__log.debug('%d resources loaded in cache' % cnt)

    def reload(self):
        self._load()

    def remove(self, resource):
        with self.__lock:
            id = resource.id

            if id in self.__resources:
                # remove from the database
                self.__db.remove_resource(id)

                # remove from the cache
                del self.__resources[id]
            else :
                raise Exception('unable to remove resource %s : not exist' % resource)

    def insert(self, resource):
        with self.__lock:
            id = resource.id

            if id not in self.__resources:
                # insertion in the database
                self.__db.insert_resource(resource.serialize())

                # insertion in the cache
                self.__resources[id] = resource
            else:
                raise Exception('unable to insert resource %s : already exist' % resource)

    def save(self, resource):
        with self.__lock:
            id = resource.id

            if id in self.__resources:
                # replace in the database
                self.__db.update_resource(resource.serialize())
            else:
                raise Exception('unable to save resource %s : not exist' % resource)

    def get(self, id):
        with self.__lock:
            return self.__resources.get(id)

    def find(self, query=None, limit=None, skip=None, sort=None):
        with self.__lock:
            resources = list(self.__resources.values())

        # self.__lock must be release from here
        if query:
            resources = [r for r in resources if query(r)]

        if isinstance(sort, string_types):
            m = re.search('^([+-]?)(.+)$', sort)
            if m is not None:
                asc = m.group(1) != '-'
                sort_attr = m.group(2)

                resources = sorted(resources, key=lambda r: getattr(r, sort_attr, None), reverse = not asc)

        offset = skip or 0

        return resources[offset:(limit + offset if limit is not None else None)]





