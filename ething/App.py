# coding: utf-8


from future.utils import text_type
from .Resource import Resource
from .Scope import Scope, ScopeValidator
from .ApiKey import ApiKey
from .Helpers import dict_recursive_update
import datetime
from .base import attr, isBool, isString, isNone, isInteger, READ_ONLY, PRIVATE, Validator




@attr('scope', validator = ScopeValidator(), default = '', description="The allowed scopes for this application (space separated list). No permissions by default.")
@attr('apikey', default = lambda _: ApiKey.generate(), mode = READ_ONLY, description="The apikey for authenticating this app.")
@attr('content', default = None, mode = PRIVATE)
@attr('icon', default = None, mode = PRIVATE)
@attr('version', validator = isString() | isNone(), default = None, description="The version of this application")
@attr('size', default = 0, mode = READ_ONLY, description="The size of the application in bytes")
@attr('mime', default = 'x-app/html', mode = READ_ONLY, description="The mime type of this app")
@attr('contentModifiedDate', default = datetime.datetime.utcnow(), mode = READ_ONLY, description="Last time the conten of this resource was modified")
class App(Resource):
    """
    Application resource representation
    """
    
    def toJson (self):
        o = super(App, self).toJson()
        o['hasIcon'] = bool(self._icon)
        return o
    
    
    def remove (self, removeChildren = False):
        
        # remove all the data from this resource
        self.ething.fs.removeFile(self._icon)
        self.ething.fs.removeFile(self._content)
        
        # remove the resource
        super(App, self).remove(removeChildren)
    
    
    
    def setIcon (self, iconData):
        # remove that file if it exists
        self.ething.fs.removeFile(self._icon)
        self._icon = None
        
        if iconData:
            self._icon = self.ething.fs.storeFile('App/%s/icon' % self.id, iconData, {
                'parent' : self.id
            })
        
        self._size = self.computeSize()
        self.save()
        return True
    
    
    def setScript (self, content, encoding = 'utf8'):
        
        # remove that file if it exists
        self.ething.fs.removeFile(self._content)
        self._content = None
        
        if content:
            
            if isinstance(content, text_type):
                content = content.encode(encoding)
            
            self._content = self.ething.fs.storeFile('App/%s/content' % self.id, content, {
                'parent' : self.id
            })
        
        self._contentModifiedDate = datetime.datetime.utcnow()
        self._size = self.computeSize()
        self.save()
        return True
    
    
    def computeSize (self):
        size = 0
        
        size += self.ething.fs.getFileSize(self._content)
        size += self.ething.fs.getFileSize(self._icon)
        
        return size
    
    
    
    def readScript (self, encoding = 'utf8'):
        contents = self.ething.fs.retrieveFile(self._content)
        
        if contents is None:
            contents = b''
        
        contents = contents.decode(encoding)
        
        return contents
    
    
    def readIcon (self):
        return self.ething.fs.retrieveFile(self._icon)
    
    


