# coding: utf-8

from ..Interface import *
from ..Device import Device
from ..utils.mime import content_to_ext


@interface
@meta(icon='photo_camera')
class Camera(Device):
    
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
            
            storage = self.core.create('resources/File', {
                'name': filename,
                'createdBy': self
            })
            
            storage.write(data)
        
        return
