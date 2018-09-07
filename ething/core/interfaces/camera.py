# coding: utf-8

from ..Interface import Interface
from ..utils.mime import content_to_ext
from ..reg import *


class Camera(Interface):
    
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
            
            storage = self.ething.create('resources/File', {
                'name': filename,
                'createdBy': self
            })
            
            storage.write(data)
        
        return
