# coding: utf-8
from .. import *


class NodeFlow (Dict):

    def __init__(self, **attributes):
        super(NodeFlow, self).__init__(mapping = {
            'flow': String(allow_empty=False),
            'node': String(allow_empty=False),
        }, **attributes)

    def to_shema(self, context = None):
        schema = super(NodeFlow, self).to_shema(context)
        schema['$component'] = 'ething.flow.node'
        schema['$filter'] = 'nodes/InputLink'
        return schema


class NodeFlowList (Array):

    def __init__(self, filter=None, **attributes):
        super(NodeFlowList, self).__init__(Dict(mapping = {
            'flow': String(allow_empty=False),
            'node': String(allow_empty=False),
        }), **attributes)
        self.filter = filter

    def to_shema(self, context = None):
        schema = super(NodeFlowList, self).to_shema(context)
        schema['$component'] = 'ething.flow.node'
        if self.filter:
            schema['$filter'] = self.filter
        return schema


@meta(icon="mdi-arrow-right-bold-outline", category="output")
@attr('targets', type=NodeFlowList('nodes/InputLink'), default=[], description='The node(s) to link with')
class OutputLink(Node):
    INPUTS = ['default']

    def main(self, **inputs):
        _msg = inputs['default']

        current_flow_id = self.flow.id
        current_node_id = self.id
        flows = self.flow.core.find(lambda r: r.typeof('resources/Flow'))
        targets = self.targets


        for flow in flows:

            for node in flow.list_nodes(): # do not use flow.nodes since the flow.nodes list may contain undeployed nodes
                if node.type == 'nodes/InputLink':
                    # is a target ?
                    for target in targets:
                        if flow.id == target['flow'] and node.id == target['node']:
                            try:
                                flow.inject(node, _msg)
                            except:
                                self.log.exception('node flow inject error')
                            break
                    else:
                        # check the sources
                        sources = node.sources
                        for source in sources:
                            if source['flow'] == current_flow_id and source['node'] == current_node_id:
                                try:
                                    flow.inject(node, _msg)
                                except:
                                    self.log.exception('node flow inject error')
                                break


@meta(icon="mdi-arrow-right-bold-outline", category="input")
@attr('sources', type=NodeFlowList('nodes/OutputLink'), default=[], description='The node(s) to link with')
class InputLink(Input):
    pass

