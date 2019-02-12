# coding: utf-8
from future.utils import integer_types, string_types
import time
import logging
from ..utils import ShortId
import gevent
from collections import MutableMapping, Mapping
try:
    import queue
except ImportError:
    import Queue as queue
import copy

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
        self._debuggers = set()
        self._context = {}
        self._error_handlers = []

    @property
    def context(self):
        return self._context

    def connect(self, src, dest):
        if not isinstance(src, Endpoint):
            node = None
            port = None

            if isinstance(src, tuple):
                node = src[0]
                if len(src) > 1:
                    port = src[1]
            elif isinstance(src, Node):
                node = src

            if isinstance(node, string_types):
                node = self.get_node(node)

            src = Endpoint(node, OUTPUT, port)
        if not isinstance(dest, Endpoint):
            node = None
            port = None

            if isinstance(dest, tuple):
                node = dest[0]
                if len(dest)>1:
                    port = dest[1]
            elif isinstance(dest, Node):
                node = dest

            if isinstance(node, string_types):
                node = self.get_node(node)

            dest = Endpoint(node, INPUT, port)

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
            for ep in endpoints:
                if ep.type == OUTPUT:
                    for c in self._connections:
                        if c.src == ep:
                            eps.append(c.dest)
                elif ep.type == INPUT:
                    for c in self._connections:
                        if c.dest == ep:
                            eps.append(c.src)
        return eps

    def stop(self):
        self._event.put(Event('quit'))

    def get_info(self, node=None):
        r = self._nodes_data
        if node is not None:
            if isinstance(node, Node):
                node = node.id
            r = self._nodes_data.get(node)
        return r

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
                'inputs': {},
                'outputs': {},
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
                self._nodes_data[node.id]['outputs'][port] = msg
                self._logger.debug('emit msg %s on port %s from node %s' % (msg, port, node))

                if endpoint is not None:
                    # propagate the message

                    connected_endpoints = self.get_connected_endpoints(endpoint)
                    connected_nodes = set()
                    for ep in connected_endpoints:
                        self._nodes_data[ep.node.id]['inputs'][ep.port] = self._nodes_data[ep.node.id]['inputs']['__last'] = msg.clone()
                        connected_nodes.add(ep.node)

                    for n in connected_nodes:
                        # self._logger.debug('receive %s' % n)
                        eps = list(filter(lambda ep: ep.node == n, connected_endpoints))
                        n.receive([ep.port for ep in eps])

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

            if node is not None:
                for d in self._debuggers:
                    self._send_info(d, node)

            if self._event.empty() and running_nodes_nb == 0:
                self._logger.debug("end of the flow")
                break

        # stop/kill any remaining running nodes
        for node in self._nodes:
            node.stop()

        tf = time.time()

        self._logger.debug("flow duration: %f sec" % (tf - t0))

        self._state = STOPPED

    def debug(self, obj, node=None):
        for d in self._debuggers:
            try:
                d.debug(obj, node=node)
            except:
                self._logger.exception('debugger exception')

    def _send_info(self, debugger, node):
        if node.id not in self._nodes_data:
            return
        try:
            debugger.info(node, self._nodes_data[node.id])
        except:
            self._logger.exception('debugger exception')

    def attach_debugger(self, debugger):
        self._debuggers.add(debugger)
        for node in self._nodes:
            self._send_info(debugger, node)

    def dettach_debugger(self, debugger):
        if debugger in self._debuggers:
            self._debuggers.remove(debugger)

    @property
    def debuggers(self):
        return list(self._debuggers)

    def handle_error(self, err, node=None):
        self._logger.error('error in node %s: %s', str(node), str(err))
        for handler in self._error_handlers:
            try:
                handler(err, node)
            except:
                self._logger.exception('error handler exception')

    def on_error(self, handler):
        self._error_handlers.append(handler)


INPUT = 'input'
OUTPUT = 'output'

class Endpoint(object):
    def __init__(self, node, type, port=None):
        self.node = node
        self.port = 'default' if port is None else str(port)
        self.type = type

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<endpoint node=%s port=%s type=%s>' % (self.node, self.port, self.type)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Endpoint):
            return self.node is other.node and self.port == other.port and self.type == other.type
        return False



class Connection(object):
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<connection %s to %s>' % (self.src, self.dest)


_pid = 0


def _get_pid():
    global _pid
    _pid += 1
    return str(_pid)


class Node(object):

    INPUTS = None
    OUTPUTS = None
    COLOR = '#4286f4'
    ICON = 'mdi-pin'
    PROPS = None
    PROPS_REQUIRED = None

    def __init__(self, flow, ntype=None, nid=None, stop_on_error=False, **other):
        self._flow = flow
        self._id = nid or ShortId.generate()
        self._type = ntype or type(self).__name__
        self._logger = logging.getLogger('ething.flow.%s' % self._id)
        self._t = {}
        self._emitted = False
        self.stop_on_error = stop_on_error

        self._flow._attach_node(self)

    @property
    def id(self):
        return self._id

    @property
    def flow(self):
        return self._flow

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<node id=%s type=%s>' % (self._id, self._type)

    def get(self, port):
        """return stored message from a given port. Return None if no message has been received."""
        return self._flow._nodes_data[self.id]['inputs'].get(port)

    def emit(self, msg=None, port=None):
        if port is None:
            if self.OUTPUTS:
                port = self.OUTPUTS[0]
            else:
                raise Exception('no output port for node %s' % self)
        if not isinstance(msg, Message):
            msg = Message(msg)
        self._emitted = True
        self._flow._event.put(Event('emmited', self, msg=msg, port=port))

    def receive(self, ports):
        input_msgs = {}
        for port in self.INPUTS:
            input_msgs[port] = self.get(port)
        self.run(**input_msgs)

    def main(self, **input_msgs):
        raise NotImplementedError()

    def run(self, **input_msgs):
        pid = _get_pid()
        self._t[pid] = gevent.spawn(self._main, input_msgs, pid)
        self._flow._event.put(Event('started', self))

    def _main(self, input_msgs, pid):
        self._logger.debug('node started pid=%s input_msgs=%s' % (pid, input_msgs))
        self._emitted = False
        err = None
        try:
            self.main(**input_msgs)
        except Exception as e:
            self._logger.exception('exception in main()')
            self.debug(e)
            self.handle_error(e)
            err = e

        self._logger.debug('node stopped')

        self._flow._event.put(Event('stopped', self, error=err))
        del self._t[pid]

    def stop(self):
        for pid in self._t:
            p = self._t[pid]
            try:
                gevent.kill(p)
            except gevent.GreenletExit:
                pass
            del self._t[pid]

    def debug(self, obj):
        self._logger.debug(str(obj))
        self._flow.debug(obj, node=self)

    def toJson(self):
        return self.id

    def handle_error(self, err):
        self._flow.handle_error(err, node=self)


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


class Message(MutableMapping):
    def __init__(self, data=None):
        self._id = ShortId.generate()
        #self._src = node
        self._ts = time.time()
        self.payload = None
        if data is not None:
            if not isinstance(data, Mapping):
                data = {'payload': data}
            self.__dict__.update(data)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<message data=%s>' % (self.__dict__,)

    def toJson(self):
        return self.__dict__

    def clone(self):
        return copy.deepcopy(self)


class Debugger(object):

    def debug(self, obj, node=None):
        pass

    def info(self, node, info):
        pass

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s>' % (type(self).__name__, )

