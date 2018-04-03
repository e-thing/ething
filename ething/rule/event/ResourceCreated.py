
from .ResourceEvent import ResourceEvent


class ResourceCreated(ResourceEvent):
    pass

if __name__ == '__main__':
    
    
    from ething.core import Core
    
    ething = Core({
        'db':{
            'database': 'test'
        }
    })
    
    r = ething.findOne()
    
    print r
    
    print ResourceCreated.emit(r)