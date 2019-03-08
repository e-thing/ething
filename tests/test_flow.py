# coding: utf-8
from ething.core.flow import *
import json
import gevent


class NodeTest(Node):
    INPUTS = ['default']

    def main(self, **inputs):
        if not hasattr(self, 'list_rec_msg'):
            setattr(self, 'list_rec_msg', [])

        self.list_rec_msg.append(inputs.get('default'))


def run_test_node(node_cls, attr=None, core=None, **inputs):

    if isinstance(node_cls, string_types):
        node_cls = get_registered_class(node_cls)

    attributes = {
        'type': get_definition_name(node_cls),
        'name': 'foo',
        'id': 'bar'
    }

    if attr is not None:
        attributes.update(attr)

    node = fromJson(node_cls, attributes, {
        'core': core
    })

    flow = FlowBase()
    flow.add_node(node)

    # patch
    emitted_msg = []

    def emit(self, msg=None, port=None):
        if port is None:
            if self.OUTPUTS:
                port = self.OUTPUTS[0]
            else:
                raise Exception('no output port for node %s' % self)
        if not isinstance(msg, Message):
            msg = Message(msg)

        emitted_msg.append((port, msg))

    setattr(node, 'emit', emit.__get__(node, type(node)))

    node.main(**inputs)

    return emitted_msg


def test_node_Function(core):
    msg = Message(time.time())

    outputs = run_test_node('nodes/Function', {
        'script': """
return msg
"""
    }, core, default=msg)

    assert outputs[0][1] is msg


def test_node_JSON(core):

    data = {
        'foo': 'bar'
    }

    json_data = json.dumps(data)


    msg0 = Message({
        'payload': data
    })
    msg1 = Message({
        'payload': json_data
    })

    outputs = run_test_node('nodes/JSON', core=core, default=msg0)
    assert outputs[0][1]['payload'] == json_data

    outputs = run_test_node('nodes/JSON', core=core, default=msg1)
    assert outputs[0][1]['payload'] == data


def test_node_Change(core):

    def generate_msg():
        return  Message({
            'payload': {
                'foo': 'bar'
            }
        })

    outputs = run_test_node('nodes/Change', attr={
        'rules': [{
            'type': 'set',
            'value': {
                'value': {'type':'msg', 'value':'payload.foo'},
                'to': {'type':'string', 'value':'hello'}
            }
        }]
    }, core=core, default=generate_msg())
    assert outputs[0][1]['payload']['foo'] == 'hello'

    outputs = run_test_node('nodes/Change', attr={
        'rules': [{
            'type': 'delete',
            'value': {
                'value': {'type': 'msg', 'value': 'payload.foo'},
            }
        }]
    }, core=core, default=generate_msg())
    assert 'foo' not in outputs[0][1]['payload']

    outputs = run_test_node('nodes/Change', attr={
        'rules': [{
            'type': 'move',
            'value': {
                'value': {'type': 'msg', 'value': 'payload.foo'},
                'to': {'type': 'msg', 'value': 'payload.cp'}
            }
        }]
    }, core=core, default=generate_msg())
    assert 'foo' not in outputs[0][1]['payload']
    assert outputs[0][1]['payload']['cp'] == 'bar'

    outputs = run_test_node('nodes/Change', attr={
        'rules': [{
            'type': 'set',
            'value': {
                'value': {'type': 'msg', 'value': 'payload'},
                'to': {'type': 'string', 'value': 'hello'}
            }
        },{
            'type': 'set',
            'value': {
                'value': {'type': 'msg', 'value': 'payload'},
                'to': {'type': 'string', 'value': 'world'}
            }
        }]
    }, core=core, default=generate_msg())
    assert outputs[0][1]['payload'] == 'world'


def test_node_Switch(core):

    msg = Message({
        'payload': 'bar'
    })

    outputs = run_test_node('nodes/Switch', attr={
        'filter': {
            'type': '==',
            'value': {
                'type': 'string',
                'value': 'bar'
            }
        }
    }, core=core, default=msg)
    assert outputs[0][0] == 'default'

    outputs = run_test_node('nodes/Switch', attr={
        'filter': {
            'type': '==',
            'value': {
                'type': 'string',
                'value': 'foo'
            }
        }
    }, core=core, default=msg)
    assert outputs[0][0] == 'fail'

    outputs = run_test_node('nodes/Switch', attr={
        'filter': {
            'type': 'type',
            'value': 'string'
        }
    }, core=core, default=msg)
    assert outputs[0][0] == 'default'

    msg = Message({
        'payload': {
            'foo': 'bar'
        }
    })

    outputs = run_test_node('nodes/Switch', attr={
        'filter': {
            'type': 'expression',
            'value': 'len($.foo) is 3'
        }
    }, core=core, default=msg)
    assert outputs[0][0] == 'default'


def test_node_Exec(core):

    msg = Message()

    outputs = run_test_node('nodes/Exec', attr={
        'command': {
            'type': 'string',
            'value': 'echo foobar'
        }
    }, core=core, default=msg)

    assert outputs[0][0] == 'stdout'
    assert outputs[0][1]['payload'].decode('utf8').strip() == 'foobar'
    assert outputs[1][0] == 'default'
    assert outputs[1][1]['payload']['code'] == 0


def test_node_Http_request(core):

    msg = Message()

    outputs = run_test_node('nodes/HttpRequest', attr={
        'url': {
            'type': 'string',
            'value': 'http://www.google.fr'
        }
    }, core=core, default=msg)

    assert outputs[0][0] == 'default'
    assert outputs[0][1]['payload']['status_code'] == 200


def test_flow(core):
    
    n_btn = fromJson('nodes/Button', {
        'id': 'id_btn',
        'name': 'btn'
    }, {
        'core': core
    })
    
    n_tst = fromJson('nodes/NodeTest', {
        'id': 'id_tst',
        'name': 'tst'
    }, {
        'core': core
    })
    
    flow = core.create('resources/Flow', {
        'name': 'test flow',
        'nodes': [n_btn, n_tst],
        'connections': [{
            'src': ['id_btn', 'default'],
            'dest': ['id_tst', 'default']
        }]
    })

    # run flow in a new process
    g = gevent.spawn(flow.run)

    time.sleep(0.5)

    flow.inject(n_btn)

    time.sleep(0.5)

    assert len(n_tst.list_rec_msg) == 1

    flow.stop()

    g.join()




