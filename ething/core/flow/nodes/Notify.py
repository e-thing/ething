# coding: utf-8
from .. import *
from ...notification import notify, MODES, INFO


@meta(icon='mdi-bell', category='notification')
@attr('mode', type=Enum(MODES), default=INFO, description="The type of the notification")
@attr('message', type=Descriptor(('text', 'template', 'msg', 'flow', 'glob', 'env')), description='The message of the notification')
class Notify(Node):
    INPUTS = ['default']

    def main(self, **inputs):
        msg = inputs.get('default')
        _context = {
            'msg': msg,
            'flow': self.flow
        }
        notify(self.core, self.message.get(**_context), mode=self.mode)
