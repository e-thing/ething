# coding: utf-8
from .. import *


attrs = {
    '$component': 'ething.flow.node',
    '$flow': '$context'
}

source_type = OneOf([
    ('all', None, 'all nodes'),
    ('nodes', Array(String(allow_empty=False), **attrs), 'selected nodes')
])

@meta(icon="mdi-alert", category="input")
@attr('source', label='Catch errors from', type=source_type, default={'type':'all'})
class Catch(Node):

    OUTPUTS = ['default']

    def main(self, **inputs):

        def handler(err, node):
            source = None

            if node is not None:
                # Cf. Wrapper_Node
                source = node.node.id

            msg = {
                'error': {
                    'message': str(err),
                    'source': source
                }
            }

            if node is not None:
                # fuse with the last message received from this node !
                last_msg = self.flow.get_info(node)['inputs'].get('__last')
                if last_msg is not None:
                    last_msg = last_msg.clone()
                    last_msg.update(msg)
                    msg = last_msg

            self.emit(msg)

        self.flow.on_error(handler)
