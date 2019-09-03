# coding: utf-8
from .. import *
from ...notification import MODES, INFO


@meta(icon='mdi-bell', category='notification')
@attr('timeout', type=Number(min=0), default=0, description="The timeout after which the notification is automatically removed. Set to 0 to make the notification persistent.")
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
        self.core.notification.notify(self.message.get(**_context), mode=self.mode, timeout=self.timeout)
