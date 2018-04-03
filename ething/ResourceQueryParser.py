
from query.Parser import Parser
from query.Field import Field
import re
import sys



def getDefaultFields():

    def hasThumbnailCompil(op,value):
        
        opstr = str(op)
        if opstr == '!=':
            value = not value
        elif opstr != '==':
            raise Exception("the operator '%s' is not accepted with the field 'hasThumbnail'" % op)
        
        if value:
            return {
                '_thumb' : {'$ne' : None}
            }
        else:
            return {
                '_thumb' : None
            }

    def hasIconCompil(op,value):
        
        opstr = str(op)
        if opstr == '!=':
            value = not value
        elif opstr != '==':
            raise Exception("the operator '%s' is not accepted with the field 'hasIcon'" % op)
        
        if value:
            return {
                '_icon' : {'$ne' : None}
            }
        else:
            return {
                '_icon' : None
            }
    
    return [
        Field('type', 'string'),
        Field('name', 'string'),
        Field('mime', 'string'),
        Field('id', 'string'),
        Field('location.latitude', 'double'),
        Field('location.longitude', 'double'),
        Field('location.altitude', 'double'),
        Field('expireAfter', 'integer'),
        Field('createdDate', 'date'),
        Field('modifiedDate', 'date'),
        Field('lastSeenDate', 'date'),
        Field('createdDate', 'date'),
        Field('createdBy', 'string'),
        Field('length', 'integer'),
        Field('size', 'integer'),
        Field('description', 'string'),
        Field('battery', 'double'),
        Field('hasThumbnail', 'bool', hasThumbnailCompil),
        Field('hasIcon', 'bool', hasIconCompil)
    ]

    
class ResourceQueryParser(Parser):
    
    fields = getDefaultFields()
    
    def __init__ (self):
        
        
        super(ResourceQueryParser, self).__init__(ResourceQueryParser.fields)
        
        self.setFieldFallback(self.fallback)
            
    def fallback(self, field):
        m = re.search('^data\.(.+)$', field)
        if m:
            return Field(field)
        
        m = re.search('^keys\.(.+)$', field)
        if m:
            return Field(field, 'integer')
        
        return None
    
    @staticmethod
    def check (expr):
        message = ''
        ok = True
        try:
            parser = ResourceQueryParser()
            parser.parse(expr)
        except:
            ok = False
            message = sys.exc_info()[1]
        
        return ok, message

if __name__ == '__main__':
    
    parser = ResourceQueryParser()
    
    print parser.parse("name == 'toto'")
    print parser.parse("hasIcon == true")
    
    ok, message = ResourceQueryParser.check("hasIcon = true")
    print ok, str(message)
    
    ok, message = ResourceQueryParser.check("  ")
    print ok, str(message)
    
