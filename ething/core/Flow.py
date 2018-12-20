# coding: utf-8

from .Resource import Resource
from .date import TzDate, utcnow
from .entity import *

from .rule.event import Event
from .rule.condition import Condition
from .rule.action import Action

from .utils.dataflow import Flow as _Flow, Node

try:
    import queue
except ImportError:
    import Queue as queue


class EventNode(Node):

    def __init__(self, flow, **other):
        self._ething = other['ething']
        self._event = other['event']
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
    def __init__(self, flow, **other):
        self._ething = other['ething']
        self._condition = other['condition']
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
    def __init__(self, flow, **other):
        self._ething = other['ething']
        self._action = other['action']
        super(ActionNode, self).__init__(flow, **other)

    def main(self, default):
        signal = default

        try:
            self._action.run(signal, self._ething)
        except:
            self._logger.exception('action exception')

        self.emit(signal)


def _model_discriminator(value, types, context):
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
        'type': Enum(['event', 'condition', 'action']),
        'model': OneOf([Event, Condition, Action], _model_discriminator)
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
                'nodes': Array(min_len=2, item_type=node_type),
                'connections': Array(min_len=1, item_type=connection_type),
            },
            **attributes
        )


@attr('flow', type=FlowData(), description="An object describing a flow.")
class Flow(Resource):

    def _parseFlow(self):
        flow_data = self.flow

        nodes_data = flow_data.get('nodes', [])
        connections_data = flow_data.get('connections', [])

        flow = _Flow()

        for node_data in nodes_data:
            type = node_data['type']
            nid = node_data['id']
            model = node_data['model']
            context = {
                'ething': self._ething
            }

            if type == 'event':
                #event = Event.unserialize(model, context=context)
                EventNode(flow, nid=nid, event=model, ething=self.ething)
            elif type == 'condition':
                #condition = Condition.unserialize(model, context=context)
                ConditionNode(flow, nid=nid, condition=model, ething=self.ething)
            elif type == 'action':
                #action = Action.unserialize(model, context=context)
                ActionNode(flow, nid=nid, action=model, ething=self.ething)
            else:
                raise Exception('invalid node type "%s"' % type)

        for connection_data in connections_data:
            src_id = connection_data['src'][0]
            src_port = connection_data['src'][1]
            dest_id = connection_data['dest'][0]
            dest_port = connection_data['dest'][1]

            flow.connect((flow.get_node(src_id), src_port), (flow.get_node(dest_id), dest_port))

        return flow


