# coding: utf-8

from .reg import get_registered_class
import logging
import threading
from future.utils import string_types
import re
import pymongo


class ResourceDbCache(object):

    def __init__ (self, core):
        self.__core = core
        self.__db = core.db
        self.__resources = dict()
        self.__log = logging.getLogger("ething.ResourceDbCache")
        self.__lock = threading.Lock()

        self._load()

    def _load(self):
        with self.__lock:

            self.__resources.clear()

            c = self.__db["resources"]

            cursor = c.find({})

            cnt = 0

            for doc in cursor:
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

    def remove(self, resource):
        with self.__lock:
            id = resource.id

            if id in self.__resources:
                # remove from the database
                c = self.__db["resources"]
                c.delete_one({'_id': id})

                # remove from the cache
                del self.__resources[id]
            else :
                raise Exception('unable to remove resource %s : not exist' % resource)

    def insert(self, resource):
        with self.__lock:
            id = resource.id

            if id not in self.__resources:
                # insertion in the database
                c = self.__db["resources"]
                try:
                    c.insert_one(resource.serialize())
                except:
                    # code 11000 on duplicate error
                    raise Exception('internal error: doc insertion failed')

                # insertion in the cache
                self.__resources[id] = resource
            else:
                raise Exception('unable to insert resource %s : already exist' % resource)

    def save(self, resource):
        with self.__lock:
            id = resource.id

            if id in self.__resources:
                # replace in the database
                c = self.__db["resources"]
                c.replace_one({'_id': id}, resource.serialize())
            else:
                raise Exception('unable to save resource %s : not exist' % resource)

    def get(self, id):
        with self.__lock:
            return self.__resources.get(id)

    def find(self, query=None, limit=None, skip=None, sort=None):
        with self.__lock:
            if query is None:
                query = {}

            if isinstance(query, string_types):
                # parse the query string
                query = self.__core.resourceQueryParser.parse(query)

            c = self.__db["resources"]

            resources = []

            if limit is None:
                limit = 0
            if skip is None:
                skip = 0

            if isinstance(sort, string_types):
                m = re.search('^([+-]?)(.+)$', sort)
                if m is not None:
                    sort = [(m.group(2), pymongo.ASCENDING if m.group(
                        1) != '-' else pymongo.DESCENDING)]
                else:
                    sort = None

            if sort is None:
                sort = [('modifiedDate', pymongo.DESCENDING)]

            cursor = c.find(query, skip=skip, limit=limit, sort=sort, projection=())

            for doc in cursor:
                id = doc['_id']

                if id in self.__resources:
                    resources.append(self.__resources[id])
                else:
                    self.__log.warning('the resource with id=%s is not found in the cache' % id)


            return resources





