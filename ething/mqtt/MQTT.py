

from ething.Device import Device, method, attr, isString, isInteger, isObject, isNone
from ething.rule.event.DeviceDataSet import DeviceDataSet

from jsonpath_rw import jsonpath, parse
import xml.etree.ElementTree as ET

import json
import os
import re



@attr('host', validator = isString(), description="The host of the MQTT broker to connect to.")
@attr('port', validator = isInteger(min=0, max=65535), default=1883, description="The port number of the MQTT broker to connect to.")
@attr('auth', validator = isNone() | isObject(user=isString(allow_empty=False), password=isString(allow_empty=False)), default=None, description="An object describing the credentials to use.")
class MQTT(Device):
    """
    MQTT Device resource representation
    """
    
    payloadContentTypes = ['application/json','text/plain','application/xml']
    
    
    def __init__(self, ething, doc):
        super(MQTT, self).__init__(ething, doc)
        self._subs = None
    
    
    @method.arg('topic', type='string', minLength = 1)
    @method.arg('payload', payload='string')
    def publish (self, topic, payload = ''):
        return self.ething.rpc.request('device.mqtt.send', self.id, topic, payload)
    
    
    def getSubscription (self):
        if self._subs is not None:
            return self.subs # cached
        
        spec = self.ething.fs.retrieveFile(self._subscription)
        self.subs = json.loads(spec) if spec else []
        return self.subs
    
    
    def setSubscription (self, subs):
        
        if isinstance(subs, list):
            for v in subs:
                
                if not isinstance(v, dict):
                    raise ValueError('sub item must be a dictionary')
                
                for k, vv in v.iteritems():
                    
                    if k == 'topic':
                        if not isinstance(vv, basestring) or len(vv)==0:
                            raise Exception('topic: must be a non empty string')
                    elif k == 'contentType':
                        if vv is not None:
                            if not isinstance(vv, basestring) or len(vv)==0:
                                raise Exception('contentType: must be a non empty string')
                            if vv not in MQTT.payloadContentTypes:
                                raise Exception('contentType: only the following types are allowed: %s' % ','.join(MQTT.payloadContentTypes))
                        
                    elif k == 'jsonPath':
                        if not isinstance(vv, basestring) and vv is not None:
                            raise Exception('jsonPath: must be a string')
                    
                    elif k == 'regexp':
                        if not isinstance(vv, basestring) and vv is not None:
                            raise Exception('regexp: must be a string')
                    elif k == 'xpath':
                        if not isinstance(vv, basestring) and vv is not None:
                            raise Exception('xpath: must be a string')
                    else:
                        raise Exception('unknown key \'%s\'' % k)
        elif subs is not None:
            raise ValueError('subs must either be None or a list')
        
        
        self._subs = None # delete cache
        
        # remove that file if it exists
        self.ething.fs.removeFile(self._subscription)
        self._subscription = None
        
        if subs:
            self._subscription = self.ething.fs.storeFile('Device/%s/subscription' % self.id, json.dumps(subs), {
                'parent' : self.id
            })
        
        self.save()
        
        return True
    
    
    def processPayload (self, topic, payload):
        
        for item in self.getSubscription():
            
            if item['topic'] == topic:
                
                data = None
                storageType = None
                storageName = os.path.basename(topic)
                
                contentType = item['contentType']
                    
                if contentType == 'application/json':
                    
                    try:
                        decoded = json.loads(payload)
                    except ValueError:
                        pass
                    else:
                        
                        if item['jsonPath']:
                            try:
                                jsonpath_expr = parse(item['jsonPath'])
                            except Exception:
                                pass
                            else:
                                results = [match.value for match in jsonpath_expr.find(decoded)]
                                if len(results):
                                    data = results[0]
                        else:
                            data = decoded
                        
                        if data:
                            if not(isinstance(data, int) or isinstance(data, float) or isinstance(data, basestring) or isinstance(data, bool)):
                                storageType = 'File'
                                storageName += '.json'
                                data = json.dumps(data, indent=4)
                    
                    
                elif contentType == 'text/plain':
                    
                    if item['regexp']:
                        
                        rec = re.compile(item['regexp'])
                        
                        for line in payload.splitlines():
                            matches = rec.search(line)
                            if matches:
                                data = matches.group(1) if (matches.groups())>0 else matches.group(0)
                                if data:
                                    
                                    if data.isnumeric():
                                        data = int(data)
                                    break
                    
                    else:
                        data = payload
                        if data.isnumeric():
                            data = int(data)
                
                elif contentType == 'application/xml':
                    
                    if not item['xpath']:
                        storageType = 'File'
                        storageName += '.xml'
                        data = payload
                    else:
                        # xpath
                        try:
                            tree = ET.fromstring(payload)
                            elements = [r.text for r in tree.findall(item['xpath'])]
                        except Exception:
                            pass
                        else:
                            
                            if len(elements)>0:
                                data = elements[0]
                                if data.isnumeric():
                                    data = int(data)
                
                
                if data:
                    
                    if not storageType:
                        if isinstance(data, basestring) and len(data)>256:
                            storageType = 'File'
                        else :
                            storageType = 'Table'
                    
                                        
                    storage = self.ething.findOne({
                        'name' : storageName,
                        'type' : storageType,
                        'createdBy' : self.id
                    })
                    
                    if not storage:
                        # create it !
                        storage = self.ething.create(storageType, {
                            'name' : storageName
                        }, self)
                    
                    
                    if storage:
                        if storageType == 'Table':
                            storage.insert({
                                'value' : data
                            })
                        elif storageType == 'File':
                            storage.write(data)
                    
                    
                    self.dispatchSignal(DeviceDataSet.emit(self, {
                        'value' : data
                    }))
                    



