# coding: utf-8
from .Resource import Resource, ResourceType
from .entity import *
from .utils.dataflow import Flow as _FlowBase, Node as _Node, Debugger, queue
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
@attr('color', type=Color())
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
        print(type, _cls, context)
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

    def test(self, signal, core):
        raise NotImplementedError()

    def main(self, n, inputs):
        msg = inputs['default']
        test_pass = False
        try:
            test_pass = self.test(msg.data, self.ething)
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

    def run(self, signal, core):
        raise NotImplementedError()

    def main(self, n, inputs):
        msg = inputs['default']

        try:
            self.run(msg.data, self.ething)
        finally:
            n.emit(msg)


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
            _Wrapper_Node(flow, node_data)

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
                        node.inject(data)
                    else:
                        raise Exception('node %s is not an input' % node)
                else:
                    raise Exception('unknown node id=%s' % node_id)


class _Wrapper_Node(_Node):

    def __init__(self, flow, node):
        self._node = node
        super(_Wrapper_Node, self).__init__(flow, nid=node.id)
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
                'timestamp': time.time()
            })


@meta(icon='mdi-android-debug-bridge')
class DebugNode(Node):
    """
    print some debug information
    """

    INPUTS = ['default']

    def main(self, n, inputs):
        n.debug(inputs.get('default'))


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

        if 'context' not in self._c:
            self._c['context'] = dict()

        try:
            eval(self.script, {
                'input': msg.data,
                'msg': msg,
                'logger': self.log,
                'ething': self.ething,
                'debug': n.debug,
                'emit': n.emit,
                'context': self._c['context']
            })
        finally:
            if not n._emitted:
                n.emit(msg)


@meta(label='If-Else', icon='mdi-help')
@attr('script', type=PythonScript(), description="The Python script. call resolve() or reject() to resolve or reject the test, respectively.")
class Test(Node):
    """Execute a python script"""

    INPUTS = ['default']
    OUTPUTS = ['default', 'fail']

    def main(self, n, inputs):
        _msg = inputs['default']

        if 'context' not in self._c:
            self._c['context'] = dict()

        def resolve(msg=None):
            if msg is None:
                msg = _msg
            n.emit(msg, port='default')

        def reject(msg=None):
            if msg is None:
                msg = _msg
            n.emit(msg, port='fail')

        try:
            eval(self.script, {
                'input': _msg.data,
                'msg': _msg,
                'logger': self.log,
                'ething': self.ething,
                'debug': n.debug,
                'reject': reject,
                'resolve': resolve,
                'context': self._c['context']
            })
        except:
            if not n._emitted:
                reject()
        else:
            if not n._emitted:
                resolve()


number_types = integer_types + (float, )


def _cast_to_number(value):
    return float(value)


def _cast_to_string(value):
    return str(value)


def _cast_to_bool(value):
    if isinstance(value, string_types):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            try:
                return bool(float(value))
            except:
                return False
    return bool(value)


def _check_number(value):
    if not isinstance(value, number_types):
        raise ValueError('not a number : %s' % value)


@meta(icon='mdi-filter')
@attr('last', mode=PRIVATE, default=None) # holds the last value
@attr('filter', type=Dict(allow_extra=True, mapping={
    'type': Enum(('exists', '==', '>', '>=', '<', '<=', 'go above', 'go under', 'regex', 'rising edge', 'falling edge'))
}))
@attr('prop_name', type=String(allow_empty=False), description='The name of the property (ie: temperature, humidity ...) to filter only the signal corresponding to this property.')
class DataFilter(ConditionNode):
    """ filter signal data """

    def test(self, signal, core):

        name = self.prop_name
        filter = self.filter
        filter_type = filter.get('type')
        value = filter.get('value')

        try:
            data = signal[name]
        except:
            return False

        if filter_type == 'exists':
            return True
        elif filter_type == '==':

            # make value the same type of data
            if isinstance(data, number_types):
                norm_value = _cast_to_number(value)
            elif isinstance(data, bool):
                norm_value = _cast_to_bool(value)
            else:
                norm_value = value

            return norm_value == data

        elif filter_type == '>':
            return _check_number(data) > _cast_to_number(value)
        elif filter_type == '>=':
            return _check_number(data) >= _cast_to_number(value)
        elif filter_type == '<':
            return _check_number(data) < _cast_to_number(value)
        elif filter_type == '<=':
            return _check_number(data) <= _cast_to_number(value)
        elif filter_type == 'regex':
            return re.search(self._cast_to_string(value), self._cast_to_string(data))
        elif filter_type == 'go above':
            _check_number(data)
            threshold = _cast_to_number(value)
            result = self.last is not None and self.last < threshold and data >= threshold
            # save the last value
            self.last = data
            return result
        elif filter_type == 'go under':
            _check_number(data)
            threshold = _cast_to_number(value)
            result = self.last is not None and self.last > threshold and data <= threshold
            # save the last value
            self.last = data
            return result
        elif filter_type == 'rising edge':
            data = _cast_to_bool(data)
            threshold = _cast_to_bool(value)
            result = self.last is not None and self.last is False and data is True
            # save the last value
            self.last = data
            return result
        elif filter_type == 'falling edge':
            data = _cast_to_bool(data)
            threshold = _cast_to_bool(value)
            result = self.last is not None and self.last is True and data is False
            # save the last value
            self.last = data
            return result
        else:
            raise Exception('invalid filter : %s' % filter_type)


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
class Scheduler(ConditionNode):
    """ Return true only within certain periods of time """

    def test(self, signal, core):
        now = datetime.datetime.now()
        weekday = now.isoweekday() # 1: monday, 7: sunday
        hour = now.hour
        minute = now.minute
        monthday = now.day

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
                    return True
            else:
                if time >= start_time or time <= end_time:
                    return True



@meta(icon='mdi-filter')
class ResourceFilter(ResourceConditionNode):
    """ filter signals that was emitted by a specific resource """

    def test(self, signal, core):
        if hasattr(signal, 'resource'):
            return signal.resource == self.resource


@meta(icon='mdi-filter')
@attr('expression', type=Expression(), description="The expression the resource must match")
@attr('resource', type=Nullable(ResourceType()), default=None, description="The resource that must match the given expression. If none, the resource is the one that emits the signal.")
class ResourceMatch(ResourceConditionNode):
    """ is true if a resource match an expression """

    def test(self, signal, core):

        r = None

        if self.resource is not None:
            r = core.get(self.resource)
        else:
            if hasattr(signal, 'resource'):
                r = signal.resource

        if r:
            return r.match(self.expression)


@abstract
@path('outputs', True)
@meta(icon='mdi-logout')
@attr('property', type=String(), default='', description="The property to expose. Leave empty to expose the whole message.")
class Output(Node):
    """Expose data"""

    INPUTS = ['default']

    def main(self, n, inputs):
        _msg = inputs['default']
        _prop = self.property
        data = _msg.data

        if _prop:
            data = data[_prop]

        _r = n.flow.resource

        with _r:
            _r.data[self.name] = json.dumps(data)


@abstract
@path('inputs', True)
@meta(icon='mdi-login')
@attr('property', type=String(), default='', description="The property to inject into the flow. Leave empty to inject the incoming data as a whole message.")
class Input(Node):
    """Expose data"""

    OUTPUTS = ['default']

    def main(self, n, inputs):

        self._m['q'] = queue.Queue()
        prop = self.property

        while True:
            data = self._m['q'].get()

            if prop:
                data = {
                    prop: data
                }

            n.emit(data)

        self._m['q'] = None


    def inject(self, data):
        _q = self._m.get('q')
        if _q is not None:
            _q.put(data)


class Button(Input):
    pass


class Label(Output):
    pass

