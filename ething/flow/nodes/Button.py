# coding: utf-8
from .. import *


@attr('data', type=Descriptor(('flow', 'glob', 'string', 'number', 'boolean', 'timestamp', 'env')), default={'type':'timestamp'}, description='The data to inject into the flow on click')
class Button(Input):

    def inject(self, data):
        data = self.data.get(flow=self.flow)
        super(Button, self).inject(data)
