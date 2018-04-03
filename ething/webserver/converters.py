
from werkzeug.routing import BaseConverter
from server_utils import getResource


def install(core, app, **kwargs):
    
    class ResourceConverter(BaseConverter):
        
        types_filter = None
        
        description = "An id representing a Resource"
        
        def to_python(self, id):
            return getResource(core, id, self.types_filter)
        
        def to_url(self, resource):
            return resource.id

    class FileConverter(ResourceConverter):
        types_filter = ['File']

    class TableConverter(ResourceConverter):
        types_filter = ['Table']

    class DeviceConverter(ResourceConverter):
        types_filter = ['Device']

    class AppConverter(ResourceConverter):
        types_filter = ['App']
    
    
    app.url_map.converters['Resource'] = ResourceConverter
    app.url_map.converters['File'] = FileConverter
    app.url_map.converters['Table'] = TableConverter
    app.url_map.converters['Device'] = DeviceConverter
    app.url_map.converters['App'] = AppConverter
    
