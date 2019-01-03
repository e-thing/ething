# coding: utf-8
from .Resource import Resource
from .entity import *
from .rule.event import Event
from .rule.condition import Condition
from .rule.action import Action
from .utils.dataflow import Flow as _Flow, Node, DebugNode, DelayNode
from .Process import Process
try:
    import queue
except ImportError:
    import Queue as queue


registered_nodes = set()


def register_node(node_cls):
    registered_nodes.add(node_cls)


def get_registered_node(type):
    for cls in registered_nodes:
        if cls.__name__ == type:
            return cls


class EventNode(Node):
    OUTPUTS = ['default']
    PROPS = {
        'event': Event.toSchema()
    }
    COLOR = '#873489'

    def __init__(self, flow, **other):
        self._ething = other['ething']
        self._event = Event.unserialize(other['event'], context={
            'ething': self._ething
        })
        super(EventNode, self).__init__(flow, **other)

    def main(self):
        q = queue.Queue()

        def push(signal):
            q.put(signal)

        self._ething.signalDispatcher.bind('*', push)

        while True:
            signal = q.get()
            if self._event.filter(signal, self._ething):
                self.emit(signal)

        self._ething.signalDispatcher.unbind('*', push)


class ConditionNode(Node):
    INPUTS = ['default']
    OUTPUTS = ['default', 'fail']
    PROPS = {
        'condition': Condition.toSchema()
    }
    COLOR = '#a91c1c'

    def __init__(self, flow, **other):
        self._ething = other['ething']
        self._condition = Condition.unserialize(other['condition'], context={
            'ething': self._ething
        })
        super(ConditionNode, self).__init__(flow, **other)

    def main(self, default):
        signal = default
        test_pass = False
        try:
            test_pass = self._condition.test(signal, self._ething)
        except:
            self._logger.exception('test exception')

        self._logger.debug('test result=%s' % test_pass)

        self.emit(signal, port='default' if test_pass else 'fail')


class ActionNode(Node):
    INPUTS = ['default']
    OUTPUTS = ['default']
    PROPS = {
        'action': Action.toSchema()
    }
    COLOR = '#346789'

    def __init__(self, flow, **other):
        self._ething = other['ething']
        self._action = Action.unserialize(other['action'], context={
            'ething': self._ething
        })
        super(ActionNode, self).__init__(flow, **other)

    def main(self, default):
        signal = default

        try:
            self._action.run(signal, self._ething)
        except:
            self._logger.exception('action exception')

        self.emit(signal)


register_node(EventNode)
register_node(ConditionNode)
register_node(ActionNode)
register_node(DebugNode)
register_node(DelayNode)


def _model_discriminator(value, types, context):
    if isinstance(value, Event):
        return types[0]
    if isinstance(value, Condition):
        return types[1]
    if isinstance(value, Action):
        return types[2]
    t = value['type']
    if t.startswith('events/'):
        return types[0]
    if t.startswith('conditions/'):
        return types[1]
    if t.startswith('actions/'):
        return types[2]


node_type = Dict(
    allow_extra=True,
    mapping={
        'id': String(allow_empty=False),
        'type': String(allow_empty=False), # Enum(['event', 'condition', 'action']),
        'model': Dict()#OneOf([Event, Condition, Action], _model_discriminator)
    }
)

connection_type = Dict(
    allow_extra=False,
    mapping={
        'src': Array(min_len=2, max_len=2, item_type=String(allow_empty=False)),
        'dest': Array(min_len=2, max_len=2, item_type=String(allow_empty=False))
    }
)


class FlowData(Dict):
    def __init__(self, **attributes):
        super(FlowData, self).__init__(
            allow_extra=False,
            mapping={
                'nodes': Array(item_type=node_type),
                'connections': Array(item_type=connection_type),
            },
            optionals=['nodes', 'connections'],
            **attributes
        )


empty_flow = {
    'nodes': [],
    'connections': []
}

class FlowProcess(Process):

    def __init__(self, flow_resource):
        super(FlowProcess, self).__init__(name='flow')
        self._flow_resource = flow_resource
        self._flow_instance = None

    def setup(self):
        self._flow_instance = self._flow_resource.parseFlow()

    def main(self):
        self._flow_instance.run()

    def end(self):
        self._flow_instance = None

    def stop(self, timeout=None):
        if self._flow_instance is not None:
            self._flow_instance.stop()
        super(FlowProcess, self).stop(timeout)


#@attr('state', mode=READ_ONLY, default='stopped', description='the current state of the flow.')
@attr('repeat', type=Boolean(), default=False, description='repeat the flow indefinitely.')
@attr('flow', type=FlowData(), default=empty_flow, description="An object describing a flow.")
class Flow(Resource):

    def deploy(self):
        self.stop() # stop any previous flow
        process = FlowProcess(self)
        process.start()
        self._m['process'] = process

    def stop(self):
        if 'process' in self._m:
            self._m['process'].stop()
            del self._m['process']

    def remove(self, removeChildren=False):
        self.stop()
        super(Flow, self).remove(removeChildren)

    def parseFlow(self):
        flow_data = self.flow

        nodes_data = flow_data.get('nodes', [])
        connections_data = flow_data.get('connections', [])

        flow = _Flow()

        for node_data in nodes_data:
            type = node_data['type']
            nid = node_data['id']
            model = node_data['model']
            node_cls = get_registered_node(type)

            if node_cls is None:
                raise Exception('unknown node type "%s"' % type)

            node_cls(flow, nid=nid, ething=self.ething, **model)

        for connection_data in connections_data:
            src_id = connection_data['src'][0]
            src_port = connection_data['src'][1]
            dest_id = connection_data['dest'][0]
            dest_port = connection_data['dest'][1]

            flow.connect((flow.get_node(src_id), src_port), (flow.get_node(dest_id), dest_port))

        return flow


