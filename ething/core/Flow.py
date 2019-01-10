# coding: utf-8
from .Resource import Resource
from .entity import *
from .rule.event import Event
from .rule.condition import Condition
from .rule.action import Action
from .utils.dataflow import Flow as _Flow, Node, DebugNode, Debugger
from .Process import Process
from .plugin import Plugin, register_plugin
try:
    import queue
except ImportError:
    import Queue as queue


registered_nodes = set()


def register_node(node_cls):
    registered_nodes.add(node_cls)


def get_registered_node(type):
    for cls in registered_nodes:
        if getattr(cls, 'NAME', cls.__name__) == type:
            return cls


register_node(DebugNode)


node_type = Dict(
    allow_extra=True,
    mapping={
        'id': String(allow_empty=False),
        'type': String(allow_empty=False),
        'model': Dict()
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

    @property
    def flow(self):
        return self._flow_instance

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

            node_cls(flow, ething=self.ething, nid=nid, **model)

        for connection_data in connections_data:
            src_id = connection_data['src'][0]
            src_port = connection_data['src'][1]
            dest_id = connection_data['dest'][0]
            dest_port = connection_data['dest'][1]

            flow.connect((flow.get_node(src_id), src_port), (flow.get_node(dest_id), dest_port))

        # attach registered debuggers
        if 'debuggers' in self._m:
            for d in self._m['debuggers']:
                flow.attach_debugger(d)

        return flow

    def attach_debugger(self, debugger):
        self.log.debug('attach debugger %s', debugger)

        if 'debuggers' not in self._m:
            self._m['debuggers'] = set()

        self._m['debuggers'].add(debugger)

        if 'process' in self._m:
            flow = self._m['process'].flow
            if flow is not None:
                flow.attach_debugger(debugger)

    def dettach_debugger(self, debugger):
        self.log.debug('dettach debugger %s', debugger)

        if 'debuggers' in self._m:
            self._m['debuggers'].remove(debugger)

        if 'process' in self._m:
            flow = self._m['process'].flow
            if flow is not None:
                flow.dettach_debugger(debugger)


class EventBaseNode(Node):
    OUTPUTS = ['default']

    def __init__(self, flow, ething, event, **other):
        self._ething = ething
        self._event = event
        super(EventBaseNode, self).__init__(flow, **other)

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


class ConditionBaseNode(Node):
    INPUTS = ['default']
    OUTPUTS = ['default', 'fail']

    def __init__(self, flow, ething, condition, **other):
        self._ething = ething
        self._condition = condition
        super(ConditionBaseNode, self).__init__(flow, **other)

    def main(self, default):
        signal = default
        test_pass = False
        try:
            test_pass = self._condition.test(signal, self._ething)
        finally:
            self._logger.debug('test result=%s' % test_pass)
            self.emit(signal, port='default' if test_pass else 'fail')


class ActionBaseNode(Node):
    INPUTS = ['default']
    OUTPUTS = ['default']

    def __init__(self, flow, ething, action, **other):
        self._ething = ething
        self._action = action
        super(ActionBaseNode, self).__init__(flow, **other)

    def main(self, default):
        signal = default

        try:
            self._action.run(signal, self._ething)
        finally:
            self.emit(signal)


def generate_node_cls(base_cls, cls):

    uri = get_definition_pathname(cls)

    def init(self, flow, ething, **other):
        other['type'] = get_definition_pathname(cls)
        instance = cls.unserialize(other, context={
            'ething': ething,
            'debugger': self.debug
        })
        base_cls.__init__(self, flow, ething, instance, **other)

    node_cls = type('%s_FlowNode' % uri.replace('/', '_'), (base_cls,), {
        '__init__': init
    })

    setattr(node_cls, 'NAME', uri)
    setattr(node_cls, 'SCHEMA', {
        '$ref': '#/' + uri
    })

    register_node(node_cls)


class FlowPlugin(Plugin):

    def setup(self):

        # register all nodes
        for cls in filter(lambda cls: get_definition_pathname(cls).startswith('events/') and not is_abstract(cls), list_registered_classes()):
            generate_node_cls(EventBaseNode, cls)

        for cls in filter(lambda cls: get_definition_pathname(cls).startswith('conditions/') and not is_abstract(cls), list_registered_classes()):
            generate_node_cls(ConditionBaseNode, cls)

        for cls in filter(lambda cls: get_definition_pathname(cls).startswith('actions/') and not is_abstract(cls), list_registered_classes()):
            generate_node_cls(ActionBaseNode, cls)

        self.core.signalDispatcher.bind('ResourceCreated', self._on_resource_created)

    def start(self):
        for f in self.core.find(lambda r: r.isTypeof('resources/Flow')):
            f.deploy()

    def _on_resource_created(self, signal):
        r = signal.resource
        if isinstance(r, Flow):
            r.deploy()


register_plugin(FlowPlugin)
