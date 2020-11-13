# coding: utf-8
from .dataflow import Flow as FlowBase, Node as NodeBase, Debugger, Message
from ..Resource import Resource, ResourceType, ResourceTypeArray, ResourceCreated
from ..plugin import PluginUpdated, PluginType
from ..reg import *
from ..utils.jsonpath import jsonpath
from ..utils.ObjectPath import ObjectPathExp, evaluate
from ..processes import Process
from ..Signal import ResourceSignal, PluginSignal
from ..dispatcher import bind, unbind
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
@attr('y', type=Number(), default=0, description='y component of the node position')
@attr('x', type=Number(), default=0, description='x component of the node position')
@attr('name', type=String(allow_empty=False), description='the name of the node')
@attr('color', type=Color(), default='#eeeeee', description='the color of the node')
@discriminate(key='type')
@attr('id', mode=READ_ONLY, type=String(allow_empty=False), description='the id of the node')
class Node(Entity, NodeBase):

    INPUTS = None
    OUTPUTS = None

    def __init__(self, value=None, context=None):

        if 'core' not in context:
            raise Exception('missing "core" in context')

        Entity.__init__(self, value, context)
        NodeBase.__init__(self, id=self.id)

    @classmethod
    def __schema__(cls, schema, context = None):
        schema['inputs'] = cls.INPUTS
        schema['outputs'] = cls.OUTPUTS
        return schema


@attr('resource', type=ResourceType(), description='the resource bind to this node')
class ResourceNode(Node):
    """
    A node bind to a :class:`ething.Resource.Resource` instance.
    """
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
                q.put(signal.__flow_msg__())

        bind('*', push, namespace=self.core.namespace)

        while True:
            self.emit(q.get())

        unbind('*', push)


connection_type = Dict(
    allow_extra=False,
    mapping={
        'src': Array(min_len=2, max_len=2, item_type=String(allow_empty=False)),
        'dest': Array(min_len=2, max_len=2, item_type=String(allow_empty=False))
    }
)


@attr('nodes', type=Array(item_type=Node), default=[], description="The list of nodes.")
@attr('connections', type=Array(item_type=connection_type), default=[], description="A list of connections")
@attr('enabled', type=Boolean(), default=True, description="Wether or not this flow is enabled")
class Flow(Resource, FlowBase):
    """
    The Flow resource represent workflow composed of nodes linked together.
    """
    def __init__(self, value=None, context=None):
        Resource.__init__(self, value, context)
        FlowBase.__init__(self, logger=self.logger)

    def deploy(self):
        """
        Deploy the flow.
        """
        self.processes["flow.%s" % self.id].restart()

    def __process__(self):
        return Process(id="flow.%s" % self.id, target=self.run, terminate=self.stop)

    def on_attr_update(self, attr, new_value, old_value):
        super(Flow, self).on_attr_update(attr, new_value, old_value)

        if attr == 'enabled':
            if new_value:
                self.processes["flow.%s" % self.id].restart()
            else:
                self.processes["flow.%s" % self.id].stop()

    def inject(self, node, data=None):
        """
        Inject data into the flow.

        :param node: a :class:`Node` instance or a node id
        :param data: The optional data to inject, may also be a message
        """
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
        if not self.enabled: return

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
    is_resource_signal = False
    is_plugin_signal = False

    if issubclass(signal_cls, ResourceSignal):
        is_resource_signal = True
    elif issubclass(signal_cls, PluginSignal):
        is_plugin_signal = True

    base_cls = SignalEventNode

    uri = get_definition_name(signal_cls)
    signal_cls_path = uri.split('/')
    signal_cls_name = signal_cls_path.pop()
    signal_cls_path = '/'.join(signal_cls_path)

    def init(self, value, context):
        context['signal'] = signal_cls
        base_cls.__init__(self, value, context)

    try:

        node_cls_dict = {
            '__init__': init,
        }

        if is_resource_signal:
            def _filter(self, signal):
                if base_cls._filter(self, signal):
                    source = self.source
                    if source.type == 'any':
                        return True
                    if source.type == 'resources':
                        resources_list = source.value
                        return signal.resource in resources_list
                    if source.type == 'expression':
                        return signal.resource.match(source.value)

            node_cls_dict['_filter'] = _filter

        node_cls = type('%s' % signal_cls_name, (base_cls,), node_cls_dict)

        prefix = 'signals/'
        if signal_cls_path.startswith(prefix):
            namespace(signal_cls_path[len(prefix):], True)(node_cls)

        meta(label=get_meta(signal_cls, 'label'), description=get_meta(signal_cls, 'description'), icon=get_meta(signal_cls, 'icon', 'mdi-signal-variant'), category=get_meta(signal_cls, 'category', 'events'))(node_cls)

        if is_resource_signal:

            if signal_cls is ResourceCreated:
                OneOf_Items = [
                    ('any',),
                    ('expression', ObjectPathExp()),
                ]
            else:
                OneOf_Items = [
                    ('any',),
                    ('resources', ResourceTypeArray(must_throw=signal_cls, min_len=1)),
                    ('expression', ObjectPathExp()),
                ]

            source_type = OneOf(OneOf_Items, **dict((('$inline', True), )))

            attr('source', type=source_type, default={'type': 'any'}, description="Select the resources that emit the signal")(node_cls)

        elif is_plugin_signal:
            if signal_cls is PluginUpdated:
                OneOf_Items = [
                    ('any',),
                    ('plugin', PluginType(must_throw=signal_cls)),
                ]

                source_type = OneOf(OneOf_Items, **dict((('$inline', True),)))

                attr('source', type=source_type, default={'type': 'any'}, description="Select the plugin that emit the signal")(node_cls)

        return node_cls
    except Exception as e:
        return


def generate_event_nodes():
    # create nodes from registered signals/conditions/actions
    for cls in filter(lambda cls: get_definition_name(cls).startswith('signals/') and not is_abstract(cls), list(list_registered_classes())):
        _generate_event_node_cls(cls)


# special nodes

@abstract
@meta(icon='mdi-logout', category="output")
@attr('data', type=Descriptor(('flow', 'glob', 'msg', 'env', 'template', 'expression')), default={'type':'msg','value':'payload'}, description='The data to expose.')
class Output(Node):
    """Expose data"""

    INPUTS = ['default']

    def main(self, **inputs):
        _msg = inputs['default']
        _data = self.data.get(flow=self.flow, msg=_msg)

        _r = self.flow
        with _r:
            _r.data[self.id] = json.dumps(_data)


@abstract
@meta(icon='mdi-login', category="input")
class Input(Node):
    """Expose data"""

    OUTPUTS = ['default']

    def main(self, **inputs):
        self._q = Queue()
        while True:
            payload = self._q.get()
            self.emit(payload)

        self._q = None


    def inject(self, data):
        if isinstance(data, Message):
            payload = data
        else:
            payload = {'payload': data}

        _q = getattr(self, '_q', None)
        if _q is not None:
            _q.put(payload)


# import all nodes
from . import nodes
