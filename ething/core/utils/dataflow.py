# coding: utf-8
from future.utils import integer_types, string_types
import time
import logging
import uuid
import gevent

try:
    import queue
except ImportError:
    import Queue as queue

_LOGGER = logging.getLogger('ething.flow')


id_types = string_types + integer_types


STOPPED = 'stopped'
RUNNING = 'running'


class Flow(object):
    def __init__(self):
        self._nodes = []
        self._connections = []
        self._event = queue.Queue()
        self._logger = _LOGGER
        self._nodes_data = {}
        self._state = STOPPED

    def connect(self, src, dest):
        self._connections.append(Connection(src, dest))

    def _attach_node(self, node):
        if node not in self._nodes:
            self._nodes.append(node)

    def get_node(self, node_id):
        for node in self._nodes:
            if node.id == node_id:
                return node

    def get_input_endpoint(self, node, port):
        for c in self._connections:
            if c.dest.node is node and c.dest.port == port:
                return c.dest

    def get_output_endpoint(self, node, port):
        for c in self._connections:
            if c.src.node is node and c.src.port == port:
                return c.src

    def get_output_endpoints(self, node):
        if not isinstance(node, Node):
            node = self.get_node(node)
        output_ep = []
        for c in self._connections:
            if c.src.node is node:
                output_ep.append(c.src)
        return output_ep

    def get_input_endpoints(self, node):
        if not isinstance(node, Node):
            node = self.get_node(node)
        inputs_ep = []
        for c in self._connections:
            if c.dest.node is node:
                inputs_ep.append(c.dest)
        return inputs_ep

    def get_connected_endpoints(self, endpoints):
        eps = []
        if endpoints is not None:
            if isinstance(endpoints, Endpoint):
                endpoints = [endpoints]
            for c in self._connections:
                if c.dest in endpoints:
                    eps.append(c.src)
                if c.src in endpoints:
                    eps.append(c.dest)
        return eps

    def stop(self):
        self._event.put(Event('quit'))

    def run(self):

        if self._state == RUNNING:
            raise Exception('flow already running')

        self._state = RUNNING

        t0 = time.time()

        # clear
        self._nodes_data.clear()
        while True:
            try:
                self._event.get(False)
            except queue.Empty:
                break

        # init
        for node in self._nodes:
            self._nodes_data[node.id] = {
                'state': None,
                'msg': {},
                'start_ts': None,
                'stop_ts': None,
                'error': None,
                'count': 0
            }

        # find starting nodes:
        starting_nodes = []
        for node in self._nodes:
            if len(self.get_input_endpoints(node)) == 0:
                starting_nodes.append(node)

        self._logger.debug("starting_nodes=%s" % starting_nodes)

        if not starting_nodes:
            self._logger.warning("empty flow")
            return

        for node in starting_nodes:
            node.run()

        running_nodes_nb = 0

        while True:
            evt = self._event.get()
            #self._logger.debug("process event=%s" % evt)

            node = evt.node
            evt_name = evt.name

            if evt_name == 'started':
                running_nodes_nb += 1
                self._nodes_data[node.id]['state'] = evt_name
                self._nodes_data[node.id]['start_ts'] = time.time()
                self._nodes_data[node.id]['count'] += 1

            elif evt_name == 'emmited':
                msg = evt['msg']
                port = evt['port']
                endpoint = self.get_output_endpoint(node, port)
                self._nodes_data[node.id]['msg'][port] = msg
                self._logger.debug('emit msg %s on port %s from node %s' % (msg, port, node))

                if endpoint is not None:
                    # propagate the message

                    connected_nodes = set()
                    for ep in self.get_connected_endpoints(endpoint):
                        connected_nodes.add(ep.node)

                    for n in connected_nodes:
                        kwargs = {}
                        for ep in self.get_input_endpoints(n):
                            msg_ = None
                            for ep_src in self.get_connected_endpoints(ep):
                                msg_src = self._nodes_data[ep_src.node.id]['msg'].get(ep_src.port)
                                if msg_src is not None:
                                    msg_ = msg_src
                                    break
                            else:
                                break
                            kwargs[ep.port] = msg_.data
                        else:
                            n.run(**kwargs)
                else:
                    # endpoint not connected
                    # nothing to propagate
                    pass

            elif evt_name == 'stopped':
                running_nodes_nb -= 1
                err = evt['error']
                self._nodes_data[node.id]['state'] = evt_name
                self._nodes_data[node.id]['stop_ts'] = time.time()
                self._nodes_data[node.id]['error'] = err

                if err is not None and node.stop_on_error:
                    self._logger.debug("stop flow on error=%s node=%s" % (err, node))
                    break

            elif evt_name == 'quit':
                break

            if self._event.empty() and running_nodes_nb == 0:
                self._logger.debug("end of the flow")
                break

        # stop/kill any remaining running nodes
        for node in self._nodes:
            node.stop()

        tf = time.time()

        self._logger.debug("flow duration: %f sec" % (tf - t0))

        self._state = STOPPED


class Endpoint(object):
    def __init__(self, node, port=None):
        if not isinstance(node, Node) and port is None:
            port = node[1]
            node = node[0]

        self.node = node
        self.port = 'default' if port is None else str(port)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<endpoint node=%s port=%s>' % (self.node, self.port)


class Connection(object):
    def __init__(self, src, dest):
        if not isinstance(src, Endpoint):
            src = Endpoint(src)
        if not isinstance(dest, Endpoint):
            dest = Endpoint(dest)
        self.src = src
        self.dest = dest

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<connection %s to %s>' % (self.src, self.dest)


class Node(object):

    INPUTS = None
    OUTPUTS = None
    COLOR = '#4286f4'
    ICON = 'mdi-pin'
    PROPS = None

    def __init__(self, flow, ntype=None, nid=None, stop_on_error=True, **other):
        self._flow = flow
        self._id = nid or uuid.uuid4()
        self._type = ntype or type(self).__name__
        self._other_props = other
        self._logger = logging.getLogger('ething.flow.%s' % self._id)
        self._t = None
        self._emitter = False
        self.stop_on_error = stop_on_error

        self._flow._attach_node(self)

    @property
    def id(self):
        return self._id

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<node id=%s type=%s>' % (self._id, self._type)

    def emit(self, msg=None, port='default'):
        if not isinstance(msg, Message):
            msg = Message(msg)
        self._emitter = True
        self._flow._event.put(Event('emmited', self, msg=msg, port=port))

    def main(self, **input_msgs):
        raise NotImplementedError()

    def run(self, **input_msgs):
        self._t = gevent.spawn(self._main, input_msgs)
        self._flow._event.put(Event('started', self))

    def _main(self, input_msgs):
        self._logger.debug('node started input_msgs=%s' % input_msgs)
        err = None
        result = None
        try:
            result = self.main(**input_msgs)
        except Exception as e:
            self._logger.exception('exception in main()')
            err = e
        else:
            if not isinstance(result, Message):
                if not self._emitter or result is not None:
                    result = Message(result)

            if result is not None:
                self.emit(result)

        self._logger.debug('node stopped')

        self._flow._event.put(Event('stopped', self, error=err))
        self._t = None

    def stop(self):
        if self._t:
            try:
                gevent.kill(self._t)
            except gevent.GreenletExit:
                pass
            self._t = None


class Event(object):
    def __init__(self, name, node=None, **other):
        self._name = name
        self._node = node
        self._ts = time.time()
        self._other = other

    @property
    def name(self):
        return self._name

    @property
    def node(self):
        return self._node

    @property
    def ts(self):
        return self._ts

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<event name=%s node=%s props=%s>' % (self._name, self._node, self._other)

    def __getitem__(self, key):
        return self._other.get(key)


class Message(object):
    def __init__(self, data=None):
        self.data = data

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<message data=%s>' % (self.data,)


class Condition(Node):

    INPUTS = ['default']
    OUTPUTS = ['default', 'fail']

    def __init__(self, flow, **other):
        self._test = other['test']
        super(Condition, self).__init__(flow, **other)

    def main(self, default, **kwargs):
        test_pass = False
        try:
            test_pass = self._test(default)
        except:
            self._logger.exception('test exception')

        self._logger.debug('test result=%s' % test_pass)

        self.emit(default, port='default' if test_pass else 'fail')


class EventSource(Node):
    OUTPUTS = ['default']

    def __init__(self, flow, **other):
        self._source = other['source']
        super(EventSource, self).__init__(flow, **other)

    def main(self):
        for v in self._source():
            self.emit(v)


class Constant(Node):
    OUTPUTS = ['default']
    PROPS = {
        'value': {}
    }

    def __init__(self, flow, **other):
        self._value = other['value']
        super(Constant, self).__init__(flow, **other)

    def main(self, **input_msgs):
        self.emit(self._value)


class FunctionNode(Node):
    INPUTS = ['default']
    OUTPUTS = ['default']

    def __init__(self, flow, **other):
        self._fn = other['fn']
        super(FunctionNode, self).__init__(flow, **other)

    def main(self, **input_msgs):
        return self._fn(**input_msgs)


class DelayNode(Node):
    INPUTS = ['default']
    OUTPUTS = ['default']
    PROPS = {
        'duration': {
            'type': 'integer',
            'minimum': 0
        }
    }

    def __init__(self, flow, **other):
        self._duration = other['duration']
        super(DelayNode, self).__init__(flow, **other)

    def main(self, **input_msgs):
        time.sleep(self._duration)


class TimerNode(Node):
    INPUTS = ['default']
    OUTPUTS = ['default']
    PROPS = {
        'interval': {
            'type': 'integer',
            'minimum': 0
        }
    }

    def __init__(self, flow, **other):
        self._interval = other['interval']
        super(TimerNode, self).__init__(flow, **other)

    def main(self):
        while True:
            self.emit(time.time())
            time.sleep(self._interval)


class DebugNode(Node):
    INPUTS = ['default']
    PROPS = {
        'message': {
            'type': 'string'
        }
    }

    def __init__(self, flow, **other):
        self._message = other.get('message', '%%msg')
        super(DebugNode, self).__init__(flow, **other)

    def main(self, default):
        self._logger.info(self._message.replace('%%msg', str(default)))


class ExitNode(Node):
    INPUTS = ['default']

    def __init__(self, flow, **other):
        super(ExitNode, self).__init__(flow, **other)

    def main(self, default):
        self._flow._event.put(Event('quit'))


if __name__ == '__main__':
    from gevent import monkey

    monkey.patch_all()

    _LOGGER.setLevel(logging.DEBUG)
    frm = logging.Formatter("%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(frm)
    _LOGGER.addHandler(stream_handler)

    flow = Flow()

    # node3 = TimerNode(flow, duration=3)
    # node2 = TimerNode(flow, duration=2)
    # node1 = TimerNode(flow, outputs=[node2, node3], duration=1)

    # node3 = DebugNode(flow, message='foobar')
    # node2 = TimerNode(flow, outputs=[node3], duration=2)
    # node1 = TimerNode(flow, outputs=[node3], duration=1)

    # test1 = Condition(flow, outputs={'fail': [node1]}, test=lambda: False)

    dbg1 = DebugNode(flow, message='dbg %%msg')


    def src():
         for i in range(5):
             time.sleep(1)
             yield i


    event1 = EventSource(flow, source=src)

    test1 = Condition(flow, test=lambda data: data > 3)

    flow.connect(event1, test1)
    flow.connect((test1, 'default'), dbg1)


    # def summ(**kwargs):
    #     return sum(kwargs.values())
    #
    # add = FunctionNode(flow, fn=summ, nid='add')
    #
    #
    # c2 = Constant(flow, value=2, nid='c2')
    # c3 = Constant(flow, value=3, nid='c3')
    # dbg2 = DebugNode(flow, message='dbg sum=%%msg', nid='dbg2')
    #
    # flow.connect(c2, (add, 0))
    # flow.connect(c3, (add, 1))
    # flow.connect(add, dbg2)

    flow.run()
