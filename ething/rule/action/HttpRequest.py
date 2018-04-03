from .. import Action
from .. import InvalidRuleException
import requests
import base64
import json

class HttpRequest(Action):
    
    @staticmethod
    def validate (attributes, context):
        
        attributes.setdefault('url', None)
        attributes.setdefault('method', 'GET')
        attributes.setdefault('auth', None)
        attributes.setdefault('headers', None)
        attributes.setdefault('body', None)
        attributes.setdefault('output', None)
        
        for key in attributes:
            
            value = attributes[key]
            
            if key == 'url':
                
                if not( isinstance(value, basestring) and len(value)>0 ):
                    raise Exception("%s: must be a non empty string." % key)
            
            elif key == 'method':
                
                if not( isinstance(value, basestring) and value.lower() in ['get', 'post', 'delete', 'put', 'patch'] ):
                    raise Exception("%s: invalid" % key)
            
            elif key == 'headers':
                
                if value is not None:
                    
                    if isinstance(value, dict):
                        for k in value:
                            if not isinstance(value[k], basestring):
                                raise Exception("%s: invalid" % key)
                    else :
                        raise Exception("%s: invalid" % key)
                
            elif key == 'auth':
                
                if value is not None:
                    if not isinstance(value, dict) or 'type' not in value or not isinstance(value['type'], basestring) or 'user' not in value or not isinstance(value['user'], basestring) or 'password' not in value or not isinstance(value['password'], basestring) :
                        raise Exception("%s: invalid" % key)
                    
                    if value['type'].lower() not in ['basic', 'digest']:
                        raise Exception("%s: invalid" % key)
                    
                    o = {
                        'type': value['type'].lower(),
                        'user': value['user'],
                        'password': value['password']
                    }
                    
                    attributes[key] = o
            
            elif key == 'body':
                
                if value is not None:
                    
                    if isinstance(value, basestring):
                        value = {
                            'type' : 'plain',
                            'value' : value
                        }
                    
                    if not isinstance(value, dict) or 'type' not in value or not isinstance(value['type'], basestring) or 'value' not in value or not isinstance(value['value'], basestring):
                        raise Exception("%s: invalid" % key)
                    
                    if value['type'].lower() not in ['plain','binary','resource']:
                        raise Exception("%s: invalid" % key)
                    
                    o = {
                        'type': value['type'].lower(),
                        'value': value['value']
                    }
                    
                    if o['type'] == 'resource':
                        
                        resource = context['ething'].get(value['value'])
                        if not resource:
                            raise Exception("%s: the resource with id '%s' does not exist." % (key,value['value']))
                        
                        if resource.type not in ['Table','File']:
                            raise Exception("%s: the resource with id '%s' must be a Table or a File." % (key,str(resource)))
                    
                    attributes[key] = o
            
            elif key == 'output':
                
                if value is not None:
                    if not( isinstance(value, basestring) and len(value)>0 ):
                        raise Exception("%s: must be resource filename." % key)
            
            else:
                raise Exception("%s: invalid" % key)
        
        return True
    
    
    
    def call(self, signal):
        body = None
        contentType = None
        
        if self['body']:
            body = self['body']
            
            if body['type'] == 'plain':
                body = body['value']
                contentType = 'text/plain'
            
            elif body['type'] ==  'binary':
                body = base64.b64decode(body['value'])
                contentType = 'application/octet-stream'
            
            elif body['type'] ==  'resource': 
                
                src = self.ething.get( body['value'] )
                if not src:
                    raise InvalidRuleException("The resource id='%s' does not exist any more" % body['value'])
                
                if src.type == 'File':
                    body = src.read()
                    contentType  = src.mime
                elif src.type == 'Table':
                    body = json.dumps(src.select(), indent = 4)
                    contentType  = 'application/json'
        
        auth = None
        
        if self['auth']:
            if self['auth']['type'] == 'basic':
                auth = requests.auth.HTTPBasicAuth(self['auth']['user'], self['auth']['password'])
            elif self['auth']['type'] == 'digest':
                auth = requests.auth.HTTPDigestAuth(self['auth']['user'], self['auth']['password'])
        
        s = requests.Session()
        if auth is not None:
            s.auth = auth
        
        #s.config['keep_alive'] = False # cf. https://stackoverflow.com/questions/10115126/python-requests-close-http-connection
        
        headers = self['headers']
        
        if contentType is not None:
            headers['content-type'] = contentType
        
        req = requests.Request(self['method'].upper(), self['url'], headers)
        prepped = s.prepare_request(req)
        
        if body:
            prepped.body = body
        
        resp = s.send(prepped,
            timeout=(6.05, 15)
        )
        
        if self['output']:
            
            text = resp.text
            
            if text:
                outf = self.ething.create('File',{
                    'name': self['output']
                })
                if outf:
                    outf.write(str(text))
        

if __name__ == '__main__':
    
    from ething.core import Core
    from ..event import Custom
    import os
    
    name = os.path.splitext(os.path.basename(__file__))[0]
    
    rule_name = 'test-rule-%s' % name
    event_name = 'test-rule-%s-event' % name
    out_name = 'test-rule-%s-out' % name
    
    core = Core({
        'db':{
            'database': 'test'
        },
        'log':{
            'level': 'debug'
        }
    })
    
    rules = core.findRules({
        'name' : rule_name
    })
    
    for r in rules:
        r.remove()
    
    files = core.find({
        'name': out_name
    })
    
    for r in files:
        r.remove()
    
    rule = core.createRule({
        'name' : rule_name,
        'events':[{
            'type': 'Custom',
            'options':{
                'name': event_name
            }
        }],
        'actions':[{
            'type': 'HttpRequest',
            'options':{
                'url': "https://jsonplaceholder.typicode.com/posts/1",
                'output': out_name
            }
        }]
    })
    
    print rule
    
    signal = Custom.emit(event_name)
    
    rule.trigger(signal)
    
    out_file = core.findOne({
        'name': out_name
    })
    
    print out_file
    
    if out_file:
        print out_file.read()
    else:
        print "ERROR: no output !"
    