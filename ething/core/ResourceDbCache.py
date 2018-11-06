# coding: utf-8

from .reg import get_registered_class
import logging
import threading
from future.utils import string_types
import re


class ResourceDbCache(object):

    def __init__ (self, core):
        self.__core = core
        self.__db = core.db
        self.__resources = dict()
        self.__log = logging.getLogger("ething.ResourceDbCache")
        self.__lock = threading.RLock()

    def load(self):
        with self.__lock:

            self.__resources.clear()

            cnt = 0
            loaded = 0

            for doc in self.__db.list_resources():
                cnt += 1
                cl = get_registered_class(doc['type'])
                if cl is not None:
                    try:
                        instance = cl.unserialize(doc, context={'ething': self.__core})

                        self.__resources[instance.id] = instance

                        loaded += 1

                    except:
                        self.__log.exception('error loading resource: name=%s type=%s id=%s' % (
                            doc.get('name'), doc.get('type'), doc.get('id')))
                else:
                    self.__log.error('unknown type: "%s"' % doc['type'])

            self.__log.debug('%d resources loaded in cache (%d skipped)' % (loaded, cnt - loaded))

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






