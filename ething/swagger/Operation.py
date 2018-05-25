# coding: utf-8
from future.utils import string_types

from ething.Helpers import reraise
import re
from .Parameter import instanciate as instanciate_parameter, StandardParameter
import sys
from ething.utils.mime import content_to_mime
import string
import random
import json
from future.utils import iteritems
try:
    from urllib.parse import quote, urlencode
except ImportError:
    from urllib import quote, urlencode


class Operation(object):

    def __init__(self, method, data, path):
        self.data = data
        self.__path = path
        self.__method = method
        self.__parameters = None

        if 'operationId' not in self.data:

            # generate a unique operation id

            opId = self.method + '_' + self.path.pathname

            opId = re.sub('[\s!@#$%^&*()_+=\[{\]};:<>|.\/?,\'"-]', '_', opId)
            opId = re.sub('((_){2,})', '_', opId)
            opId = re.sub('^_*', '', opId)
            opId = re.sub('_*$', '', opId)

            self.__name = opId

        else:
            self.__name = self.data.get('operationId')

    @property
    def root(self):
        return self.path.root

    @property
    def name(self):
        return self.__name

    @property
    def method(self):
        return self.__method

    @property
    def description(self):
        return self.data.get('description', '')

    @property
    def path(self):
        return self.__path

    @property
    def produces(self):
        return self.data.get('produces', self.root.produces)

    @property
    def consumes(self):
        c = self.data.get('consumes', self.root.consumes)
        if len(c) == 0:
            c.append('application/json')  # default to json
        return c

    @property
    def parameters(self):

        if self.__parameters is None:

            self.__parameters = []

            for paramobj in self.data.get('parameters', []):
                self.__parameters.append(instanciate_parameter(paramobj, self))

            self.__parameters += self.path.parameters

        return self.__parameters

    def createRequest(self, data=None, **options):

        # build the url
        schemes = self.data.get('schemes', self.root.schemes)
        if len(schemes) == 0:
            schemes = ['http']

        if 'scheme' in options and options['scheme'] in schemes:
            scheme = options['scheme']
        else:
            scheme = schemes[0]

        url = '%s://%s%s%s' % (scheme, self.root.host,
                               self.root.basePath, self.path.pathname)

        method = self.method
        query = []
        formData = {}
        headers = {}
        body = None
        hasFiles = 0
        hasContentTypeHeader = False
        hasBody = False

        consumes = self.consumes

        defaultContentType = 'application/json' if 'application/json' in consumes else consumes[0]
        contentType = options.get('requestContentType', defaultContentType)

        for param in self.parameters:

            hasValue = data is not None and param.name in data
            hasDefault = isinstance(
                param, StandardParameter) and param.hasDefault
            value = None

            if hasValue:
                value = data[param.name]
            else:
                if param.isRequired:
                    if hasDefault:
                        value = param.defaultValue
                    else:
                        raise Exception(
                            "missing required param: '%s'" % param.name)
                else:
                    continue

            # validate the incomming data
            try:
                v = param.validate(value)
            except Exception as e:
                reraise(type(e), type(e)("invalid param: '%s' : %s" %
                                         (param.name, str(e))), sys.exc_info()[2])
            else:
                value = v

            where = param.where

            if where == 'formData':

                if param.type == 'file':
                    
                    mime = content_to_mime(value, 'text/plain')

                    formData[param.name] = {
                        "type": "file",
                        "content": str(value),
                        "filename": 'file'+str(hasFiles),
                        "mime": mime
                    }

                    hasFiles += 1
                else:

                    formData[param.name] = {
                        "type": "text",
                        "content": str(value)
                    }

            elif where == 'query':

                if param.collectionFormat == 'multi':
                    for v in value:
                        query.append(quote(param.name.encode(
                            "utf-8"))+'='+quote(str(v).encode("utf-8")))
                else:
                    query.append(quote(param.name.encode("utf-8")) +
                                 '='+quote(str(value).encode("utf-8")))

            elif where == 'header':

                if param.name.lower() == 'content-type':
                    contentType = str(value)
                    hasContentTypeHeader = True

                headers[param.name] = value

            elif where == 'path':
                url = re.sub('\{%s\}' % param.name, urlencode(value), url)

            elif where == 'body':

                hasBody = True
                body = value

        query = '&'.join(query)

        if len(query) > 0:
            if '?' in url:
                url += '&' + query
            else:
                url += '?' + query

        # prepare the body
        if formData:
            # there is a form data
            # check if the consumes mime type are compatible

            if contentType != 'application/x-www-form-urlencoded' and contentType != 'multipart/form-data':
                # not compatible !
                # find a compatible contentType in the consumes list
                if 'application/x-www-form-urlencoded' in consumes:
                    contentType = 'application/x-www-form-urlencoded'
                elif 'multipart/form-data' in consumes:
                    contentType = 'multipart/form-data'
                else:
                    contentType = 'application/x-www-form-urlencoded'  # default

            if hasFiles:
                contentType = 'multipart/form-data'  # no choice !

            if contentType == 'multipart/form-data':
                # multipart form ...
                boundary = ''.join(random.choice(
                    string.ascii_lowercase + string.digits) for _ in range(10))
                contentType += '; boundary=' + boundary
                body = Operation.generateMultipartFormDataBody(
                    formData, boundary)

            else:

                p = []
                for k, v in iteritems(formData):
                    p.append(quote(k.encode("utf-8"))+'=' +
                             quote(str(v).encode("utf-8")))

                body = '&'.join(p)

        elif hasBody:

            if 'json' in contentType:

                if not body:
                    body = '{}'

                if not isinstance(body, string_types):
                    body = json.dumps(body, indent=4)

            elif isinstance(body, string_types):
                pass
            else:
                raise Exception(
                    "unable to encode the body data into '%s'" % contentType)

        if body and not hasContentTypeHeader:
            headers['Content-Type'] = contentType

        return {
            'method': method.upper(),
            'url': url,
            'headers': headers,
            'body': body
        }

    @staticmethod
    def generateMultipartFormDataBody(data, boundary):

        body = ''
        eol = "\r\n"

        for name, d in iteritems(data):

            body += '--' + boundary + eol

            if d['type'] == 'file':
                body += 'Content-Disposition: form-data; name="' + \
                    name + '"; filename="' + d['filename'] + '"' + eol
                body += 'Content-Type: ' + d['mime'] + eol
                body += d['content'] + eol
            else:
                body += 'Content-Disposition: form-data; name="' + name + '"' + eol + eol
                body += d['content'] + eol

        body += "--" + boundary + "--" + eol + eol

        return body
