

import json
from .Path import Path
from jsonderef import JsonDeref


dereferencer = JsonDeref(raise_on_not_found=True, not_found=None,requests_timeout=10)


class Reader(object):
    
    
    def __init__ (self, specification):
        
        self.__operations = None
        self.__paths = None
        self.data = None # hold the specification
        
        if isinstance(specification, basestring):
            self.data = json.loads(specification)
        
        
        elif isinstance(specification, dict):
            self.data = specification
        
        else:
            raise ValueError('must be a dict or a string')
        
        if self.version is not None and self.version != '2.0':
            raise Exception('Only 2.0 swagger specification is accepted.')
        
        #resolve the reference !
        self.data = dereferencer.deref(self.data, max_deref_depth=10)
        
    
    @property
    def version (self):
        return self.data.get('swagger', None)
    
    @property
    def produces (self):
        return self.data.get('produces', [])
    
    @property
    def consumes (self):
        return self.data.get('consumes', [])
    
    @property
    def host (self):
        return self.data.get('host', 'localhost')
    
    @property
    def basePath (self):
        return self.data.get('basePath', '')
    
    @property
    def schemes (self):
        s = self.data.get('schemes', [])
        if len(s)==0:
            s.append('http')
        return s
    
    @property
    def url (self):
        return '%s://%s%s' % (self.schemes[0], self.host, self.basePath)
    
    
    # return all the operations
    @property
    def operations (self):
        
        if self.__operations is None:
            
            self.__operations = []
            
            for path in self.paths:
                
                self.__operations += path.operations
                
        return self.__operations
    
    
    def findOperationById (self, id):
        for op in self.operations:
            if op.name == id:
                return op
        return None;
    
    @property
    def paths (self):
        
        if self.__paths is None:
            self.__paths = []
            for pathname, pathobj in self.data.get('paths', {}).iteritems():
                self.__paths.append(Path(pathname, pathobj, self))
        
        return self.__paths
    
    
    


if __name__ == '__main__':
    
    def get(url):
        import urllib, json
        response = urllib.urlopen(url)
        return json.loads(response.read())
    
    reader = Reader(get('https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v2.0/json/petstore.json'))
    
    for op in reader.operations:
        
        schema = None
        
        if op.parameters:
            schema = {
                'type': 'object',
                'required': [],
                'additionalProperties': False,
                'properties': {}
            }
            
            for param in op.parameters:
                schema['properties'][param.name] = param.toJsonSchema()
                if param.isRequired:
                    schema['required'].append(param.name)
            
                
            
            
            response = None
            produces = op.produces
            if produces:
                response = produces[0]
            
            print param.name
            print schema
    
    

