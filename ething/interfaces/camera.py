# coding: utf-8

from ething.meta import interface, method, iface
from ething.utils.mime import content_to_ext


@interface
class Camera(iface):
    
    @method.return_type('image/*')
    def snapshot(self):
        """
        get a snapshot.
        """
        raise NotImplementedError()
        
    
    @method.arg('filename', type='string')
    def snapshot_and_save(self, filename):
        """
        get a snapshot and store it
        """
        data = self.snapshot()
        
        if data:
        
            if filename is None:
                # get extension from content
                filename = "image.%s" % content_to_ext(data, 'jpg')
            
            storage = self.ething.create('File', {
                'name': filename,
                'createdBy': self
            })
            
            storage.write(data)
        
        return
