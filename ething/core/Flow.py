# coding: utf-8
from .Resource import Resource, ResourceType
from .entity import *
from .utils.dataflow import Flow as _FlowBase, Node as _Node, Debugger, queue
from .utils.jsonpath import jsonpath
from .Process import Process
from .plugin import Plugin, register_plugin
from .Signal import Signal, ResourceSignal
from .query import Expression
try:
    import queue
except ImportError:
    import Queue as queue
import time
from croniter import croniter
import pytz
import logging
import datetime
import json
import os
import collections


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

    def main(self, n, inputs):
        raise NotImplementedError()

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


@path('events', True)
@abstract
class EventNode(Node):
    OUTPUTS = ['default']


@path('conditions', True)
@abstract
class ConditionNode(Node):
    INPUTS = ['default']
    OUTPUTS = ['default', 'fail']

    def test(self, msg, flow, core):
        raise NotImplementedError()

    def main(self, n, inputs):
        msg = inputs['default']
        test_pass = False
        try:
            test_pass = self.test(msg, n.flow, self.ething)
        finally:
            self.log.debug('test result=%s' % test_pass)
            n.emit(msg, port='default' if test_pass else 'fail')


@abstract
class ResourceConditionNode(ConditionNode, ResourceNode):
    pass


@path('actions', True)
@abstract
class ActionNode(Node):
    INPUTS = ['default']
    OUTPUTS = ['default']

    def run(self, msg, core):
        raise NotImplementedError()

    def main(self, n, inputs):
        msg = inputs['default']
        res = None

        try:
            res = self.run(msg, self.ething)
        finally:
            n.emit(msg if res is None else {'payload':res})


@abstract
class ResourceActionNode(ActionNode, ResourceNode):
    pass


@abstract
class SignalEventNode(EventNode):
    def __init__(self, value=None, context=None):

        if 'signal' not in context:
            raise Exception('missing "signal" in context')

        super(SignalEventNode, self).__init__(value, context)

    def _filter(self, signal):
        return isinstance(signal, self._context['signal'])

    def main(self, n, inputs):
        q = queue.Queue()

        def push(signal):
            if self._filter(signal):
                q.put(signal)

        self.ething.signalDispatcher.bind('*', push)

        while True:
            n.emit(q.get())

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
            Wrapper_Node(flow, node_data)

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
        return self._node.main(self, input_msgs)


def generate_event_node_cls(signal_cls):

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

    meta(label=get_meta(signal_cls, 'label'), description=get_meta(signal_cls, 'description'), icon=get_meta(signal_cls, 'icon'))(node_cls)

    if issubclass(signal_cls, ResourceSignal):
        attr('resource', type=ResourceType(must_throw=signal_cls))(node_cls)

    return node_cls


class FlowPlugin(Plugin):

    def setup(self):

        # create nodes from registered signals/conditions/actions

        for cls in filter(lambda cls: get_definition_pathname(cls).startswith('signals/') and not is_abstract(cls), list(list_registered_classes())):
            generate_event_node_cls(cls)

        self.core.signalDispatcher.bind('ResourceCreated', self._on_resource_created)

    def start(self):
        for f in self.core.find(lambda r: r.isTypeof('resources/Flow')):
            f.deploy()

    def _on_resource_created(self, signal):
        r = signal.resource
        if isinstance(r, Flow):
            r.deploy()


register_plugin(FlowPlugin)




class CronExpr(String):
    def __init__(self, **attr):
        super(CronExpr, self).__init__(allow_empty=False, **attr)

    def toSchema(self, context=None):
        schema = super(CronExpr, self).toSchema(context)
        schema['format'] = 'cron'
        return schema


@attr('expression', type=CronExpr())
class CronEventNode(EventNode):
    """
    is emitted periodically at fixed times, dates, or intervals
    """

    def main(self, n, inputs):

        local_tz = self.ething.config.get('timezone', 'UTC')
        local_ts = datetime.datetime.utcfromtimestamp(time.time())
        if local_tz != 'UTC':
            local_ts = pytz.utc.localize(local_ts).astimezone(pytz.timezone(local_tz))

        iter = croniter(self.expression, local_ts, day_or=False)

        while True:
            next_ts = iter.get_next()
            time.sleep(next_ts - time.time())
            n.emit({
                'payload': time.time()
            })


@meta(icon='mdi-android-debug-bridge')
@attr('print_log', label='print to log', type=Boolean(), default=False, description='print the debug information in the log')
@attr('print_debug_window', label='print to debug window', type=Boolean(), default=True, description='print the debug information in the debug window')
@attr('output', type=Descriptor(('fullmsg', 'msg')), default={'type':'msg','value':'payload'}, description='Select the message property to display.')
class DebugNode(Node):
    """
    print some debug information
    """

    INPUTS = ['default']

    def main(self, n, inputs):
        _msg = inputs.get('default')
        _data = self.output.get(msg=_msg, flow=n.flow)
        if self.print_debug_window:
            n.debug(_data)
        if self.print_log:
            self.log.info(str(_data))


@meta(icon='mdi-clock')
@attr('duration', type=Integer(min=1), default=1000, description="The waiting duration in milliseconds.")
class Sleep(Node):
    """ Wait a certain amount of time """

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, n, inputs):
        time.sleep(self.duration / 1000.)
        n.emit(inputs.get('default'))


class PythonScript(String):
    def __init__(self, **attributes):
        super(PythonScript, self).__init__(**attributes)

    def toSchema(self, context = None):
        schema = super(PythonScript, self).toSchema(context)
        schema['format'] = 'text/x-python'
        return schema


@meta(icon='mdi-function')
@attr('script', type=PythonScript(), description="The Python script.")
class Function(Node):
    """Execute a python script"""

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, n, inputs):
        msg = inputs['default']
        context = n.flow.context

        try:
            formatted = []
            for l in self.script.splitlines():
                formatted.append('  ' + l)

            formatted = '\n'.join(formatted)

            formatted = """
import collections

def __main():
""" + formatted + """

res = __main()
if res is not None:
  if isinstance(res, collections.Sequence):
    for r in res:
      emit(r)
  else:
    emit(res)

"""
            exec(formatted, {
                'msg': msg,
                'logger': self.log,
                'ething': self.ething,
                'debug': n.debug,
                'emit': n.emit,
                'context': context
            })

        except:
            pass


def item_to_daily_time(hour, minute):
    return hour * 3600 + minute * 60

def item_to_weekly_time(weekday, hour, minute):
    if weekday == 0:
        weekday = 7
    return weekday * 86400 + hour * 3600 + minute * 60

def item_to_monthly_time(monthday, hour, minute):
    return monthday * 86400 + hour * 3600 + minute * 60


SchedulerDataItem = Dict(
    optionals = ('monthday', 'weekday'),
    mapping = {
        'monthday': Integer(min=1, max=31),
        'weekday': Integer(min=1, max=7),
        'hour': Integer(min=0, max=23),
        'minute': Integer(min=0, max=59)
    }
)


class SchedulerData(Array):
    def __init__(self, **attributes):
        super(SchedulerData, self).__init__(
            Dict(
                mapping=OrderedDict([
                    ('mode', Enum(['daily', 'weekly', 'monthly'])),
                    ('start', SchedulerDataItem),
                    ('end', SchedulerDataItem)
                ])
            ),
            min_len=1,
            **attributes
        )

    def toSchema(self, context = None):
        schema = super(SchedulerData, self).toSchema(context)
        schema['format'] = 'scheduler'
        return schema


@meta(icon='mdi-clock-outline')
@attr('items', type=SchedulerData())
class Scheduler(Node):
    """ Return true only within certain periods of time """

    INPUTS = ['default']
    OUTPUTS = ['default', 'fail']

    def main(self, n, inputs):
        msg = inputs.get('default')

        now = datetime.datetime.now()
        weekday = now.isoweekday() # 1: monday, 7: sunday
        hour = now.hour
        minute = now.minute
        monthday = now.day
        res = False

        for item in self.items:

            mode = item.get('mode')
            start = item.get('start')
            end = item.get('end')

            if mode == 'daily':
                start_time = item_to_daily_time(start.get('hour'), start.get('minute'))
                end_time = item_to_daily_time(end.get('hour'), end.get('minute'))
                time = item_to_daily_time(hour, minute)

            elif mode == 'weekly':
                start_time = item_to_weekly_time(start.get('weekday'), start.get('hour'), start.get('minute'))
                end_time = item_to_weekly_time(end.get('weekday'), end.get('hour'), end.get('minute'))
                time = item_to_weekly_time(weekday, hour, minute)

            elif mode == 'monthday':
                start_time = item_to_weekly_time(start.get('monthday'), start.get('hour'), start.get('minute'))
                end_time = item_to_weekly_time(end.get('monthday'), end.get('hour'), end.get('minute'))
                time = item_to_weekly_time(monthday, hour, minute)
            else:
                continue

            if start_time <= end_time:
                if time >= start_time and time <= end_time:
                    res = True
                    break
            else:
                if time >= start_time or time <= end_time:
                    res = True
                    break

        n.emit(msg, port='default' if res else 'fail')



@meta(icon='mdi-filter')
class ResourceFilter(ResourceConditionNode):
    """ filter signals that was emitted by a specific resource """

    def test(self, msg, flow, core):
        return msg.get('resource') == core.get(self.resource)


@meta(icon='mdi-filter')
@attr('expression', type=Expression(), description="The expression the resource must match")
@attr('resource', type=Nullable(ResourceType()), default=None, description="The resource that must match the given expression. If none, the resource is the one that emits the message.")
class ResourceMatch(ResourceConditionNode):
    """ is true if a resource match an expression """

    def test(self, msg, flow, core):

        r = None

        if self.resource is not None:
            r = core.get(self.resource)
        else:
            r = msg.get('resource')

        if r:
            return r.match(self.expression)


@abstract
@path('outputs', True)
@meta(icon='mdi-logout')
@attr('data', type=Descriptor(('flow', 'glob', 'msg', 'env')), default={'type':'msg','value':'payload'}, description='The data to expose.')
class Output(Node):
    """Expose data"""

    INPUTS = ['default']

    def main(self, n, inputs):
        _msg = inputs['default']
        _data = self.data.get(flow=n.flow, msg=_msg)

        _r = n.flow.resource
        with _r:
            _r.data[self.name] = json.dumps(_data)


@abstract
@path('inputs', True)
@meta(icon='mdi-login')
class Input(Node):
    """Expose data"""

    OUTPUTS = ['default']

    def main(self, n, inputs):

        self._m['q'] = queue.Queue()

        while True:
            data = self._m['q'].get()
            n.emit({'payload': data})

        self._m['q'] = None


    def inject(self, flow, data):
        _q = self._m.get('q')
        if _q is not None:
            _q.put(data)


@attr('data', type=Descriptor(('flow', 'glob', 'string', 'number', 'boolean', 'timestamp', 'env')), default={'type':'timestamp'}, description='The data to inject into the flow on click')
class Button(Input):

    def inject(self, flow, data):
        data = self.data.get(flow=flow)
        super(Button, self).inject(flow, data)


class Label(Output):
    pass


@path('functions', True)
@meta(icon='mdi-json')
class JSON(Node):
    """convert to/from JSON"""

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, n, inputs):
        data = inputs['default'].get('payload')

        if isinstance(data, string_types):
            n.emit({'payload': json.loads(data)})
        else:
            n.emit({'payload': json.dumps(data)})


@path('general', True)
@meta(icon='mdi-comment-text-outline')
class Comment(Node):
    def main(self, n, inputs):
        pass


rule_item = OneOf([
    ('set', Dict(mapping=OrderedDict([
        ('value', Descriptor(('msg', 'flow', 'glob'))),
        ('to', Descriptor(('msg', 'flow', 'glob', 'string', 'number', 'boolean', 'timestamp', 'env')))
    ]))),
    ('change', Dict(mapping=OrderedDict([
        ('value', Descriptor(('msg', 'flow', 'glob'))),
        ('search', Descriptor(('msg', 'flow', 'glob', 'string', 'number', 'boolean', 'env'))),
        ('replace', Descriptor(('msg', 'flow', 'glob', 'string', 'number', 'boolean', 'timestamp', 'env')))
    ]))),
    ('delete', Dict(mapping=OrderedDict([
        ('value', Descriptor(('msg', 'flow', 'glob')))
    ]))),
    ('move', Dict(mapping=OrderedDict([
        ('value', Descriptor(('msg', 'flow', 'glob'))),
        ('to', Descriptor(('msg', 'flow', 'glob')))
    ])))
])

@meta(icon='mdi-pencil')
@attr('rules', type=Array(rule_item), default=[{
    'type': 'set',
    'value': {
        'value': {'type':'msg', 'value':'payload'},
        'to': {'type':'string', 'value':''}
    }
}])
class Change(Node):
    """
    Set, change, delete or move properties of a message, flow context or global context.

    The node can specify multiple rules that will be applied in the order they are defined.
    """

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, n, inputs):
        _msg = inputs['default']
        _context = {
            'msg': _msg,
            'flow': n.flow
        }

        for rule in self.rules:
            rule_type = rule.type
            rule_data = rule.value

            if rule_type == 'set':
                val = rule_data['to'].get(**_context)
                rule_data['value'].set(val, **_context)
            elif rule_type == 'change':
                val = rule_data['to'].get(**_context)
                pattern = rule_data['search'].get(**_context)
                repl = rule_data['replace'].get(**_context)
                new_val = re.search(pattern, repl, val)
                rule_data['value'].set(new_val, **_context)
            elif rule_type == 'delete':
                rule_data['value'].delete(**_context)
            elif rule_type == 'move':
                val = rule_data['value'].get(**_context)
                rule_data['to'].set(val, **_context)
                rule_data['value'].delete(**_context)

        n.emit(_msg)


value_descriptor = Descriptor(('msg', 'flow', 'glob', 'string', 'number', 'env', 'prev'))
value_str_descriptor = Descriptor(('msg', 'flow', 'glob', 'string', 'env', 'prev'))

filter_type = OneOf([
    ('==', value_descriptor),
    ('!=', value_descriptor),
    ('<' , value_descriptor),
    ('<=', value_descriptor),
    ('>' , value_descriptor),
    ('>=', value_descriptor),
    ('between', Dict(mapping=OrderedDict([
        ('min', value_descriptor),
        ('max', value_descriptor)
    ])), 'is between'),
    ('contains', value_str_descriptor),
    ('regex', value_str_descriptor, 'matches regex'),
    ('true', None, 'is true'),
    ('false', None, 'is false'),
    ('none', None, 'is none'),
    ('not_none', None, 'is not none'),
    ('type', Enum(['string','number','boolean','array','object','none']), 'is of type'),
    ('empty', None, 'is empty'),
    ('not_empty', None, 'is not empty'),
    ('go_above', Descriptor(('msg', 'flow', 'glob', 'number', 'env')), 'go above'),
    ('go_under', Descriptor(('msg', 'flow', 'glob', 'number', 'env')), 'go under'),
    ('rising_edge', None, 'rising edge'),
    ('falling_edge', None, 'falling edge')
])

@meta(icon='mdi-filter')
@attr('last', mode=PRIVATE, default=None) # holds the last value
@attr('filter', type=filter_type, default={'type':'==', 'value':{'type':'string', 'value':''}})
@attr('data', type=Descriptor(('flow', 'glob', 'msg')), default={'type':'msg','value':'payload'}, description='The data to filter.')
class Switch(Node):
    """
    Route messages based on their property values or sequence position
    """

    def main(self, n, inputs):
        old_val = self.last
        _msg = inputs['default']
        _context = {
            'msg': _msg,
            'flow': n.flow,
            'prev_val': old_val
        }

        filter_type = self.filter.type
        val = self.data.get(**_context)
        res = None

        try:
            if filter_type == '==':
                filter_value = self.filter.value.get(**_context)
                res = val == filter_value
            elif filter_type == '!=':
                filter_value = self.filter.value.get(**_context)
                res = val != filter_value
            elif filter_type == '<':
                filter_value = self.filter.value.get(**_context)
                res = val < filter_value
            elif filter_type == '<=':
                filter_value = self.filter.value.get(**_context)
                res = val <= filter_value
            elif filter_type == '>':
                filter_value = self.filter.value.get(**_context)
                res = val > filter_value
            elif filter_type == '>=':
                filter_value = self.filter.value.get(**_context)
                res = val >= filter_value
            elif filter_type == 'between':
                min_val = self.filter.value['min'].get(**_context)
                max_val = self.filter.value['max'].get(**_context)
                res = val >= min_val and val <= max_val
            elif filter_type == 'contains':
                filter_value = self.filter.value.get(**_context)
                res = filter_value in val
            elif filter_type == 'regex':
                filter_value = self.filter.value.get(**_context)
                res = bool(re.search(filter_value, val))
            elif filter_type == 'true':
                res = val is True
            elif filter_type == 'false':
                res = val is False
            elif filter_type == 'none':
                res = val is None
            elif filter_type == 'not_none':
                res = val is not None
            elif filter_type == 'type':
                t = self.filter.value.get(**_context)
                if t=='string':
                    res = isinstance(val, string_types)
                elif t=='number':
                    res = isinstance(val, number_types)
                elif t=='boolean':
                    res = isinstance(val, bool)
                elif t=='array':
                    res = isinstance(val, collections.Sequence)
                elif t=='object':
                    res = isinstance(val, collections.Mapping)
                elif t=='none':
                    res = val is None
            elif filter_type == 'empty':
                res = len(val) == 0
            elif filter_type == 'not_empty':
                res = len(val) != 0
            elif filter_type == 'go_above':
                filter_value = self.filter.value.get(**_context)
                res = old_val is not None and old_val < filter_value and val >= filter_value
            elif filter_type == 'go_under':
                filter_value = self.filter.value.get(**_context)
                res = old_val is not None and old_val > filter_value and val <= filter_value
            elif filter_type == 'rising_edge':
                res = old_val is not None and old_val == False and val == True
            elif filter_type == 'falling_edge':
                res = old_val is not None and old_val == True and val == False
        except:
            res = None

        # save the last value
        self.last = val

        n.emit(_msg, port='default' if res else 'fail')



