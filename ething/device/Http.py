# coding: utf-8
from future.utils import string_types


from future.utils import iteritems
from ething.Device import Device, method, attr, isString, isNone, isObject, READ_ONLY, PRIVATE, Validator
from ething.utils import pingable
from ething.Helpers import dict_recursive_update
from ething.Scope import Scope, ScopeValidator
from ething.ApiKey import ApiKey
import json
from ething.swagger import Reader
import requests
try:
    from urllib.parse import urlparse, urlsplit, urlencode, parse_qs, urlunparse
except ImportError:
    from urlparse import urlparse, urlsplit, parse_qs, urlunparse
    from urllib import urlencode



@pingable('url')
@attr('url', validator = isString(allow_empty = False, regex = '^https?://'), description="The URL of the device.")
@attr('scope', validator = ScopeValidator(), default = '', description="The allowed scopes for this device (space separated list). Restrict the Http api access. Default to an empty string (no access).")
@attr('auth', validator = isObject(user=isString(allow_empty=False), password=isString(allow_empty=False), type=isString(enum=['basic', 'digest'])) | isNone(), default=None, description="An object describing the authentication method to use on HTTP request.")
@attr('apikey', default = lambda _: ApiKey.generate(), mode = READ_ONLY, description="The apikey for authenticating this device.")
@attr('specification', default = None, mode = PRIVATE)
class Http(Device):
    """
    Http Device resource representation
    """
    
    @property
    def isServer (self):
        return self.url is not None
    
    
    @property
    def isAuthenticate (self):
        return bool(self.auth)
    
    @property
    def authMode (self):
        return self.auth.get('type', None) if self.auth else None
    
    @property
    def authUser (self):
        return self.auth.get('user', None) if self.auth else None
    
    @property
    def authPassword (self):
        return self.auth.get('password', None) if self.auth else None
    
    
    def dynamic_interface(self):
        
        if not self.isServer:
            return
        
        reader = Reader(self.getSpecification())
        
        def generate_dyn_method(op):
            
            response = None
            produces = op.produces
            if produces:
                response = produces[0]
            
            
            @method.bind_to(self)
            @method.name(op.name)
            @method.description(op.description)
            @method.return_type(response)
            def req(self, **kwargs):
                
                request_ = op.createRequest(kwargs)
                
                # cf. https://gist.github.com/gear11/8006132
                
                r = self.make_request(request_['url'], method = request_['method'], headers = request_['headers'], body = request_['body'])
                
                content_type = r.headers.get('content-type', None)
                content_length = int(r.headers.get('content-length', 0))
                isjson = False
                stream = False
                
                if content_type == 'application/json':
                    isjson = True
                    stream = False
                else:
                    if content_length > 15000:
                        stream = True
                
                if stream:
                    
                    def generate():
                        try:
                            for chunk in r.iter_content(1024):
                                yield chunk
                        except:
                            r.close()
                    
                    return generate()
                
                else:
                    if isjson:
                        try:
                            content = json.loads(r.content)
                        except:
                            content = r.content
                    else:
                        content = r.content
                        
                    return content
            
            
            if op.parameters:
                
                # call the method.arg in reverse order to preserve the original argument order (first decorator call correspond to the last argument !)
                # 
                # method.arg('arg2')(req)
                # method.arg('arg1')(req)
                # 
                # is equivalent to
                #
                # @method.arg('arg1')
                # @method.arg('arg2')
                # def req(arg1, arg2):
                #    ...
                for param in reversed(op.parameters): 
                    schema = param.toJsonSchema()
                    method.arg(param.name, required=param.isRequired, **schema)(req)
            
        
        
        for op in reader.operations:
            generate_dyn_method(op)
        
    
    
    def make_request(self, path, method = 'get', headers = {}, body = None ):
        
        auth = None
        
        ref = urlsplit(self.url)
        new = urlsplit(path)
        
        # join path
        path = ref.path.rstrip('/') + '/' + new.path.lstrip('/')
        
        # join the query string
        query = dict_recursive_update({}, parse_qs(new.query), parse_qs(ref.query))
        
        if self.isAuthenticate and self.authMode == 'query':
            query['user'] = [self.authUser]
            query['password'] = [self.authPassword]
        
        q = []
        for k,vv in iteritems(query):
            for v in vv:
                q.append((k,v))
        
        query = urlencode(q)
        
        url = urlunparse((ref.scheme, ref.netloc, path, '', query, ''))
        
        self.ething.log.debug("Http request: %s", url)
        
        if self.isAuthenticate:
            if self.authMode == 'basic':
                auth = requests.auth.HTTPBasicAuth(self.authUser, self.authPassword)
            elif self.authMode == 'digest':
                auth = requests.auth.HTTPDigestAuth(self.authUser, self.authPassword)
        
        s = requests.Session()
        if auth is not None:
            s.auth = auth
        
        #s.config['keep_alive'] = False # cf. https://stackoverflow.com/questions/10115126/python-requests-close-http-connection
        
        req = requests.Request(method.upper(), url, headers)
        prepped = s.prepare_request(req)
        
        if body:
            prepped.body = body
        
        resp = s.send(prepped,
            timeout=(6.05, 15)
        )
        
        self.ething.log.debug("Http response: %d", resp.status_code)
        
        return resp


    @staticmethod
    def checkSpecification (ething, swagger):
        
        # sanitize the specification
        if isinstance(swagger, string_types):
            swagger = json.loads(swagger)
        
        
        swagger = dict_recursive_update({
            'swagger': '2.0',
            'info':{
                'title': "untitled",
                'version': '0.1.0'
            },
            'paths': {}
        }, swagger)
        
        r = requests.post("http://online.swagger.io/validator/debug", data=json.dumps(swagger))
        
        if r.status_code != 200:
            raise Exception('unable to reach http://online.swagger.io/validator/debug')
        
        # the response must be valid JSON data containing an array of errors
        try:
            result = json.loads(r.text)
        except:
            result = None
        
        if result:
            
            if isinstance(result, dict) and 'schemaValidationMessages' in result:
                message = result['schemaValidationMessages'][0]['message']
            else:
                message = 'unknown error'
            
            raise Exception('invalid swagger API specification: %s' % message)
        
        
        return swagger
    
    
    
    def setSpecification (self, swagger):
        if not self.isServer:
            raise Exception('this device has no URL set')
        
        if isinstance(swagger, string_types):
            # must be json !
            swagger = json.loads(swagger)
        
        self.ething.fs.removeFile(self._specification)
        self._specification = None
        
        if swagger is not None:
            self._specification = self.ething.fs.storeFile('Device/%s/specification' % self.id, json.dumps(swagger).encode('utf8'), {
                'parent' : self.id
            })
        
        self.update_interface()
    
    
    
    def getSpecification (self):
        if not self.isServer:
            raise Exception('this device has no API specification')
        spec = self.ething.fs.retrieveFile(self._specification)
        return json.loads(spec.decode('utf8')) if spec else self.defaultSpecification()
    
    
    def defaultSpecification(self):
        # return a minimal swagger object
        return {
            'swagger': '2.0',
            'info':{
                'title': self.name,
                'version': '0.1.0'
            },
            'paths': {}
        }
    
    
    



