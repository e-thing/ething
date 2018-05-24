# coding: utf-8
from future.utils import string_types


import json
from .Path import Path
from jsonderef import JsonDeref
from future.utils import iteritems

dereferencer = JsonDeref(raise_on_not_found=True,
                         not_found=None, requests_timeout=10)


class Reader(object):

    def __init__(self, specification):

        self.__operations = None
        self.__paths = None
        self.data = None  # hold the specification

        if isinstance(specification, string_types):
            self.data = json.loads(specification)

        elif isinstance(specification, dict):
            self.data = specification

        else:
            raise ValueError('must be a dict or a string')

        if self.version is not None and self.version != '2.0':
            raise Exception('Only 2.0 swagger specification is accepted.')

        # resolve the reference !
        self.data = dereferencer.deref(self.data, max_deref_depth=10)

    @property
    def version(self):
        return self.data.get('swagger', None)

    @property
    def produces(self):
        return self.data.get('produces', [])

    @property
    def consumes(self):
        return self.data.get('consumes', [])

    @property
    def host(self):
        return self.data.get('host', 'localhost')

    @property
    def basePath(self):
        return self.data.get('basePath', '')

    @property
    def schemes(self):
        s = self.data.get('schemes', [])
        if len(s) == 0:
            s.append('http')
        return s

    @property
    def url(self):
        return '%s://%s%s' % (self.schemes[0], self.host, self.basePath)

    # return all the operations

    @property
    def operations(self):

        if self.__operations is None:

            self.__operations = []

            for path in self.paths:

                self.__operations += path.operations

        return self.__operations

    def findOperationById(self, id):
        for op in self.operations:
            if op.name == id:
                return op
        return None

    @property
    def paths(self):

        if self.__paths is None:
            self.__paths = []
            for pathname, pathobj in iteritems(self.data.get('paths', {})):
                self.__paths.append(Path(pathname, pathobj, self))

        return self.__paths
