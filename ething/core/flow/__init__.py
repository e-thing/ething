# coding: utf-8
from .dataflow import Flow as FlowBase, Node as NodeBase, Debugger, Message
from ..Resource import Resource, ResourceType
from ..reg import *
from ..utils.jsonpath import jsonpath
from ..utils.ObjectPath import ObjectPathExp, evaluate
from ..utils.weak_ref import weak_ref
from ..Process import Process
from ..Signal import ResourceSignal
from queue import Queue
import time
import os
import json
import jinja2


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


class ObjectPathDescriptor(DescriptorData):
    value_type = ObjectPathExp()

    def get(self, **context):
        return evaluate(self.value, context['msg'])


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


class TextDescriptor(ValueDescriptor):
    value_type = Text(default='')


class TemplateDescriptor(DescriptorData):
    value_type = Text(default='', description='''
Based on [Jinja2](http://jinja.pocoo.org) templating engine.
The message payload can be accessible through `{{ msg.payload }}`.
''')

    def get(self, **context):
        template = jinja2.Template(self.value)
        return template.render(**context)


# TODO: JSON


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
        'text': TextDescriptor,
        'template': TemplateDescriptor,
        'glob': GlobalDescriptor,
        'timestamp': TimestampDescriptor,
        'msg': MsgDescriptor,
        'fullmsg': FullMsgDescriptor,
        'prev': PrevValueDescriptor,
        'expression': ObjectPathDescriptor
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


@namespace('nodes')
@attr('y', type=Number(), default=0)
@attr('x', type=Number(), default=0)
@attr('name', type=String(allow_empty=False))
@attr('color', type=Color(), default='#eeeeee')
@discriminate(key='type')
@attr('id', mode=READ_ONLY, type=String(allow_empty=False))
class Node(Entity, NodeBase):

    INPUTS = None
    OUTPUTS = None

    def __init__(self, value=None, context=None):

        if 'core' not in context:
            raise Exception('missing "core" in context')

        Entity.__init__(self, value, context)
        NodeBase.__init__(self, id=self.id)

    @property
    def log(self):
        return self._logger

    def __schema__(cls, schema, context = None):
        schema['inputs'] = cls.INPUTS
        schema['outputs'] = cls.OUTPUTS
        return schema


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
        return isinstance(signal, self.signal)

    def main(self, **inputs):
        q = Queue()

        def push(signal):
            if self._filter(signal):
                q.put(signal.toFlowMessage())

        self.core.signalDispatcher.bind('*', push)

        while True:
            self.emit(q.get())

        self.core.signalDispatcher.unbind('*', push)


@abstract
@attr('resource', description="The resource that emits the signal")
class ResourceSignalEventNode(SignalEventNode, ResourceNode):

    def _filter(self, signal):
        if super(ResourceSignalEventNode, self)._filter(signal):
            return self.resource is None or signal.resource == self.resource  # None means all resources


connection_type = Dict(
    allow_extra=False,
    mapping={
        'src': Array(min_len=2, max_len=2, item_type=String(allow_empty=False)),
        'dest': Array(min_len=2, max_len=2, item_type=String(allow_empty=False))
    }
)


@attr('nodes', type=Array(item_type=Node), default=[], description="The list of nodes.")
@attr('connections', type=Array(item_type=connection_type), default=[], description="A list of connections")
class Flow(Resource, FlowBase):

    def __init__(self, value=None, context=None):
        Resource.__init__(self, value, context)
        FlowBase.__init__(self, logger=self.log)

    def deploy(self):
        self._processes["flow.%s" % self.id].restart()

    def __process__(self):
        p = Process(id="flow.%s" % self.id, target=self.run, terminate=self.stop)
        self._process = weak_ref(p)
        return p

    def inject(self, node, data=None):
        if isinstance(node, string_types):
            node_id = node
            node = self.get_node(node_id)
            if node is None:
                raise Exception('unknown node id=%s' % node_id)

        if isinstance(node, Input):
            node.inject(data)
        else:
            raise Exception('node %s is not an input' % node)

    def run(self):
        self.clear()

        # rebuild the flow
        for node in self.nodes:
            self.add_node(node)

        for connection_data in self.connections:
            src_id = connection_data['src'][0]
            src_port = connection_data['src'][1]
            dest_id = connection_data['dest'][0]
            dest_port = connection_data['dest'][1]

            self.connect((src_id, src_port), (dest_id, dest_port))

        return super(Flow, self).run()


def _generate_event_node_cls(signal_cls):

    if issubclass(signal_cls, ResourceSignal):
        base_cls = ResourceSignalEventNode
    else:
        base_cls = SignalEventNode

    uri = get_definition_name(signal_cls)
    signal_cls_path = uri.split('/')
    signal_cls_name = signal_cls_path.pop()
    signal_cls_path = '/'.join(signal_cls_path)

    def init(self, value, context):
        context['signal'] = signal_cls
        base_cls.__init__(self, value, context)

    try:
        node_cls = type('%s' % signal_cls_name, (base_cls,), {
            '__init__': init
        })

        prefix = 'signals/'
        if signal_cls_path.startswith(prefix):
            namespace(signal_cls_path[len(prefix):], True)(node_cls)

        meta(label=get_meta(signal_cls, 'label'), description=get_meta(signal_cls, 'description'), icon=get_meta(signal_cls, 'icon', 'mdi-signal-variant'), category=get_meta(signal_cls, 'category', 'events'))(node_cls)

        if issubclass(signal_cls, ResourceSignal):
            attr('resource', type=ResourceType(must_throw=signal_cls))(node_cls)

        return node_cls
    except:
        return


def generate_event_nodes():
    # create nodes from registered signals/conditions/actions
    for cls in filter(lambda cls: get_definition_name(cls).startswith('signals/') and not is_abstract(cls), list(list_registered_classes())):
        _generate_event_node_cls(cls)


# special nodes

@abstract
@meta(icon='mdi-logout', category="output")
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
@meta(icon='mdi-login', category="input")
class Input(Node):
    """Expose data"""

    OUTPUTS = ['default']

    def main(self, **inputs):

        self._q = Queue()

        while True:
            data = self._q.get()
            self.emit({'payload': data})

        self._q = None


    def inject(self, data):
        _q = getattr(self, '_q', None)
        if _q is not None:
            _q.put(data)


# import all nodes
from . import nodes