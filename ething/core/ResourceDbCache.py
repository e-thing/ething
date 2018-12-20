# coding: utf-8

from .reg import get_registered_class
from .utils.lock import SecureRLock
from .utils import object_sort
import logging
import threading
from future.utils import string_types
import re
# from pkg_resources import parse_version


class ResourceDbCache(object):

    def __init__ (self, core):
        self.__core = core
        self.__db = core.db
        self.__resources = dict()
        self.__log = logging.getLogger("ething.ResourceDbCache")
        self.__lock = SecureRLock(name='DbCache') # threading.RLock()

    def load(self):
        with self.__lock:

            self.__resources.clear()

            # db_version = self.__db.kv_get('VERSION')
            # current_version = self.__core.version
            # need_upgrade = False
            # if db_version is not None and current_version != 'unknown':
            #     if current_version == db_version:
            #         pass # nothing to do !
            #     elif parse_version(current_version) > parse_version(db_version):
            #         # need to upgrade
            #         need_upgrade = True
            #     else:
            #         raise Exception('Version mismatch : the database version (%s) is newer than your ething version (%s). You need to upgrade ething.' % (db_version, current_version))
            #
            # self.__log.info('DB version: %s , need_upgrade: %s' % (db_version, need_upgrade))
            #
            # if need_upgrade:
            #     self.__log.info('upgrading database %s --> %s' % (db_version, current_version))
            #     for doc in self._list_resources():
            #         cl = get_registered_class(doc['type'])
            #         if cl is not None:
            #             try:
            #                 cl.upgrade(doc, db_version, current_version, self.__core)
            #             except:
            #                 self.__log.warning('error upgrading resource: name=%s type=%s id=%s , this resource is no more compatible with your current version' % (
            #                     doc.get('name'), doc.get('type'), doc.get('id')))
            #                 self._remove_resource(doc.get('id'))
            #             else:
            #                 self._update_resource(doc)
            #
            #     self.__db.kv_set('VERSION', current_version)
            # elif db_version is None and current_version != 'unknown':
            #     self.__db.kv_set('VERSION', current_version)

            cnt = 0
            loaded = 0

            for doc in self._list_resources():
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
        self.load()

    def unload(self):
        with self.__lock:
            self.__resources.clear()

    def remove(self, resource):
        with self.__lock:
            id = resource.id

            if id in self.__resources:
                # remove from the database
                self._remove_resource(id)

                # remove from the cache
                del self.__resources[id]
            else :
                raise Exception('unable to remove resource %s : not exist' % resource)

    def insert(self, resource):
        with self.__lock:
            id = resource.id

            if id not in self.__resources:
                # insertion in the database
                self._insert_resource(resource.serialize())

                # insertion in the cache
                self.__resources[id] = resource
            else:
                raise Exception('unable to insert resource %s : already exist' % resource)

    def save(self, resource):
        with self.__lock:
            id = resource.id

            if id in self.__resources:
                # replace in the database
                self._update_resource(resource.serialize())
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

                resources = object_sort(resources, key=lambda r: getattr(r, sort_attr, None), reverse = not asc)

        offset = skip or 0

        return resources[offset:(limit + offset if limit is not None else None)]

    def _list_resources(self):
        if not self.__db.table_exists('resources'):
            self.__db.create_table('resources')

        return self.__db.get_table_rows('resources')

    def _update_resource(self, resource):
        self.__db.update_table_row('resources', resource['id'], resource, return_old=False)

    def _insert_resource(self, resource):
        self.__db.insert_table_row('resources', resource)

    def _remove_resource(self, resource_id):
        self.__db.remove_table_row('resources', resource_id, return_old=False)



