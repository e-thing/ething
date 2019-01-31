# coding: utf-8
from .dataflow import Flow as _FlowBase, Node as _Node, Debugger, Message
from ..Resource import Resource, ResourceType
from ..entity import *
from ..utils.jsonpath import jsonpath
from ..Process import Process
from ..plugin import Plugin, register_plugin
from ..Signal import ResourceSignal
try:
    import queue
except ImportError:
    import Queue as queue
import time
import logging
import os
import json


number_types = integer_types + (float, )


def _jsonpath_find(jp, obj):
    res = jsonpath(jp, obj)
    if len(res) == 1:
        return res[0]
    elif len(res) > 1:
        return res
    else:
        return None


class JsonPathType(String):

    def __init__(self, allow_root=False, **attributes):
        super(JsonPathType, self).__init__(allow_empty=allow_root, **attributes)


class DescriptorData(AllOfItemData):
    value_type = None
    label = None

    def get(self, **context):
        raise NotImplementedError()

    def set(self, value, **context):
        raise NotImplementedError()

    def delete(self, **context):
        raise NotImplementedError()


class EnvDescriptor(DescriptorData):
    label = 'env variable'
    value_type = String(allow_empty=False)

    def get(self, **context):
        return os.environ.get(self.value)

    def set(self, value, **context):
        os.environ[self.value] = str(value)

    def delete(self, **context):
        del os.environ[self.value]


class GlobalDescriptor(DescriptorData):
    label = 'global.'
    value_type = JsonPathType()

    def get(self, **context):
        return _jsonpath_find(self.value, globals())

    def set(self, value, **context):
        jsonpath(self.value, globals(), action='set', args=(value,))

    def delete(self, **context):
        jsonpath(self.value, globals(), action='delete')


class FlowDescriptor(DescriptorData):
    label = 'flow.'
    value_type = JsonPathType()

    def get(self, **context):
        return _jsonpath_find(self.value, context['flow'].context)

    def set(self, value, **context):
        jsonpath(self.value, context['flow'].context, action='set', args=(value,))

    def delete(self, **context):
        jsonpath(self.value, context['flow'].context, action='delete')


class MsgDescriptor(DescriptorData):
    label = 'msg.'
    value_type = JsonPathType()

    def get(self, **context):
        return _jsonpath_find(self.value, context['msg'])

    def set(self, value, **context):
        jsonpath(self.value, context['msg'], action='set', args=(value,))

    def delete(self, **context):
        jsonpath(self.value, context['msg'], action='delete')


class FullMsgDescriptor(DescriptorData):
    label = 'complete message object'

    def get(self, **context):
        return context['msg']


class PrevValueDescriptor(DescriptorData):
    label = 'previous value'

    def get(self, **context):
        return context['prev_val']


class ValueDescriptor(DescriptorData):
    def get(self, **context):
        return self.value


class StringDescriptor(ValueDescriptor):
    value_type = String(default='')


class NumberDescriptor(ValueDescriptor):
    value_type = Number(default=0)


class BooleanDescriptor(ValueDescriptor):
    value_type = Boolean(default=False)


# TODO: JSON
# TODO: JSONata  cf: https://nodered.org/docs/user-guide/messages#split


class TimestampDescriptor(DescriptorData):
    def get(self, **context):
        return time.time()


class Descriptor(OneOf):

    MODES = {
        'env': EnvDescriptor,
        'flow': FlowDescriptor,
        'string': StringDescriptor,
        'number': NumberDescriptor,
        'boolean': BooleanDescriptor,
        'glob': GlobalDescriptor,
        'timestamp': TimestampDescriptor,
        'msg': MsgDescriptor,
        'fullmsg': FullMsgDescriptor,
        'prev': PrevValueDescriptor
    }

    def __init__(self, modes, **attributes):

        items = []
        for mode_name in modes:
            mode_cls = self.MODES.get(mode_name)
            if mode_cls is None:
                raise Exception('unknow mode %s' % mode_name)
            items.append(AllOfItem(mode_name, mode_cls.value_type, label=mode_cls.label, data_cls=mode_cls))

        attributes['$inline'] = True
        super(Descriptor, self).__init__(items, **attributes)


class _Flow(_FlowBase):

    def __init__(self, resource):
        super(_Flow, self).__init__()
        self.__resource = resource

    @property
    def resource(self):
        return self.__resource

    def run(self):
        self.resource.data = {}
        return super(_Flow, self).run()


@path('nodes')
@abstract
@attr('y', type=Number(), default=0)
@attr('x', type=Number(), default=0)
@attr('name', type=String(allow_empty=False))
@attr('color', type=Color(), default='#eeeeee')
@attr('type', mode=READ_ONLY, type=String(allow_empty=False))
@attr('id', mode=READ_ONLY, type=String(allow_empty=False))
class Node(Entity):

    INPUTS = None
    OUTPUTS = None

    def __init__(self, value=None, context=None):

        if 'ething' not in context:
            raise Exception('missing "ething" in context')

        Entity.__init__(self, value, context)

        object.__setattr__(self, '_Node__ething', context.get('ething'))
        object.__setattr__(self, '_Node__log', logging.getLogger('ething.%s.%s' % (self.type.replace('/', '.'), value.get('id'))))

    @property
    def ething(self):
        return self.__ething

    @property
    def log(self):
        return self.__log

    def main(self, **inputs):
        raise NotImplementedError()

    def _attach(self, flow):
        self._m['flow'] = flow
        self._m['node'] = Wrapper_Node(flow, self)

    def emit(self, *args, **kwargs):
        return self._m['node'].emit(*args, **kwargs)

    def debug(self, *args, **kwargs):
        return self._m['node'].debug(*args, **kwargs)

    @property
    def flow(self):
        return self._m['flow']

    @classmethod
    def unserialize(cls, data, context=None):
        type = data.get('type')
        _cls = get_registered_class(type)
        if _cls is None:
            raise Exception('unknown type "%s"' % type)
        return Entity.unserialize.__func__(_cls, data, context)

    @classmethod
    def fromJson(cls, data, context=None):
        type = data.get('type')
        _cls = get_registered_class(type)
        if _cls is None:
            raise Exception('unknown type "%s"' % type)
        return Entity.fromJson.__func__(_cls, data, context)

    @classmethod
    def toSchema(cls, context = None):
        schema = super(Node, cls).toSchema(context)
        schema['inputs'] = cls.INPUTS
        schema['outputs'] = cls.OUTPUTS
        return schema


@abstract
@attr('resource', type=ResourceType())
class ResourceNode(Node):
    pass


@abstract
class SignalEventNode(Node):
    OUTPUTS = ['default']

    def __init__(self, value=None, context=None):

        if 'signal' not in context:
            raise Exception('missing "signal" in context')

        super(SignalEventNode, self).__init__(value, context)

    def _filter(self, signal):
        return isinstance(signal, self._context['signal'])

    def main(self, **inputs):
        q = queue.Queue()

        def push(signal):
            if self._filter(signal):
                q.put(signal.toFlowMessage())

        self.ething.signalDispatcher.bind('*', push)

        while True:
            self.emit(q.get())

        self.ething.signalDispatcher.unbind('*', push)


@abstract
@attr('resource', description="The resource that emits the signal")
class ResourceSignalEventNode(SignalEventNode, ResourceNode):

    def _filter(self, signal):
        if super(ResourceSignalEventNode, self)._filter(signal):
            return self._resource is None or signal.resource.id == self.resource  # None means all resources


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
                'nodes': Array(item_type=Node),
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

        flow = _Flow(self)

        for node_data in nodes_data:
            node_data._attach(flow)

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

    def inject(self, node_id, data):
        if 'process' in self._m:
            flow = self._m['process'].flow
            if flow is not None:
                nodeflow = flow.get_node(node_id)
                if nodeflow is not None:
                    node = nodeflow.node
                    if isinstance(node, Input):
                        node.inject(flow, data)
                    else:
                        raise Exception('node %s is not an input' % node)
                else:
                    raise Exception('unknown node id=%s' % node_id)


class Wrapper_Node(_Node):

    def __init__(self, flow, node):
        self._node = node
        super(Wrapper_Node, self).__init__(flow, nid=node.id)
        self.INPUTS = node.INPUTS
        self.OUTPUTS = node.OUTPUTS

    @property
    def node(self):
        return self._node

    def __str__(self):
        return '<node id=%s name=%s type=%s>' % (self._id, self._node.name, self._node.type)

    def main(self, **input_msgs):
        return self._node.main(**input_msgs)


def _generate_event_node_cls(signal_cls):

    if issubclass(signal_cls, ResourceSignal):
        base_cls = ResourceSignalEventNode
    else:
        base_cls = SignalEventNode

    uri = get_definition_pathname(signal_cls)
    signal_cls_path = uri.split('/')
    signal_cls_name = signal_cls_path.pop()
    signal_cls_path = '/'.join(signal_cls_path)

    def init(self, value, context):
        context['signal'] = signal_cls
        base_cls.__init__(self, value, context)

    node_cls = type('%s' % signal_cls_name, (base_cls,), {
        '__init__': init
    })

    prefix = 'signals/'
    if signal_cls_path.startswith(prefix):
        path(signal_cls_path[len(prefix):], True)(node_cls)

    meta(label=get_meta(signal_cls, 'label'), description=get_meta(signal_cls, 'description'), icon=get_meta(signal_cls, 'icon'), category=get_meta(signal_cls, 'category'))(node_cls)

    if issubclass(signal_cls, ResourceSignal):
        attr('resource', type=ResourceType(must_throw=signal_cls))(node_cls)

    return node_cls


class FlowPlugin(Plugin):

    def setup(self):

        # create nodes from registered signals/conditions/actions

        for cls in filter(lambda cls: get_definition_pathname(cls).startswith('signals/') and not is_abstract(cls), list(list_registered_classes())):
            _generate_event_node_cls(cls)

        self.core.signalDispatcher.bind('ResourceCreated', self._on_resource_created)

    def start(self):
        for f in self.core.find(lambda r: r.isTypeof('resources/Flow')):
            f.deploy()

    def _on_resource_created(self, signal):
        r = signal.resource
        if isinstance(r, Flow):
            r.deploy()


register_plugin(FlowPlugin)


# special nodes

@abstract
@meta(icon='mdi-logout')
@attr('data', type=Descriptor(('flow', 'glob', 'msg', 'env')), default={'type':'msg','value':'payload'}, description='The data to expose.')
class Output(Node):
    """Expose data"""

    INPUTS = ['default']

    def main(self, **inputs):
        _msg = inputs['default']
        _data = self.data.get(flow=self.flow, msg=_msg)

        _r = self.flow.resource
        with _r:
            _r.data[self.name] = json.dumps(_data)


@abstract
@meta(icon='mdi-login')
class Input(Node):
    """Expose data"""

    OUTPUTS = ['default']

    def main(self, **inputs):

        self._m['q'] = queue.Queue()

        while True:
            data = self._m['q'].get()
            self.emit({'payload': data})

        self._m['q'] = None


    def inject(self, flow, data):
        _q = self._m.get('q')
        if _q is not None:
            _q.put(data)

# import all nodes
from . import nodes
