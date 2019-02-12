# coding: utf-8
from ething.core.flow.dataflow import Flow as _Flow
from ething.core.flow import *
import json


class _Test_Node_Wrapper(Wrapper_Node):

    def __init__(self, *args, **kwargs):
        super(_Test_Node_Wrapper, self).__init__(*args, **kwargs)
        self.emitted_msg = []

    def emit(self, msg=None, port=None):
        if port is None:
            if self.OUTPUTS:
                port = self.OUTPUTS[0]
            else:
                raise Exception('no output port for node %s' % self)
        if not isinstance(msg, Message):
            msg = Message(msg)

        self.emitted_msg.append((port, msg))


def _test_node(node_cls, attr=None, core=None, **inputs):

    if isinstance(node_cls, string_types):
        node_cls = get_registered_class(node_cls)

    attributes = {
        'type': get_definition_name(node_cls),
        'name': 'foo',
        'id': 'bar'
    }

    if attr is not None:
        attributes.update(attr)

    node = Node.fromJson(attributes, {
        'ething': core
    })._attach(_Flow(), cls=_Test_Node_Wrapper)

    node.main(**inputs)

    return node.emitted_msg


def test_node_Function(core):
    msg = Message(time.time())

    outputs = _test_node('nodes/Function', {
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

    outputs = _test_node('nodes/JSON', core=core, default=msg0)
    assert outputs[0][1]['payload'] == json_data

    outputs = _test_node('nodes/JSON', core=core, default=msg1)
    assert outputs[0][1]['payload'] == data


def test_node_Change(core):

    def generate_msg():
        return  Message({
            'payload': {
                'foo': 'bar'
            }
        })

    outputs = _test_node('nodes/Change', attr={
        'rules': [{
            'type': 'set',
            'value': {
                'value': {'type':'msg', 'value':'payload.foo'},
                'to': {'type':'string', 'value':'hello'}
            }
        }]
    }, core=core, default=generate_msg())
    assert outputs[0][1]['payload']['foo'] == 'hello'

    outputs = _test_node('nodes/Change', attr={
        'rules': [{
            'type': 'delete',
            'value': {
                'value': {'type': 'msg', 'value': 'payload.foo'},
            }
        }]
    }, core=core, default=generate_msg())
    assert 'foo' not in outputs[0][1]['payload']

    outputs = _test_node('nodes/Change', attr={
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

    outputs = _test_node('nodes/Change', attr={
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

    outputs = _test_node('nodes/Switch', attr={
        'filter': {
            'type': '==',
            'value': {
                'type': 'string',
                'value': 'bar'
            }
        }
    }, core=core, default=msg)
    assert outputs[0][0] == 'default'

    outputs = _test_node('nodes/Switch', attr={
        'filter': {
            'type': '==',
            'value': {
                'type': 'string',
                'value': 'foo'
            }
        }
    }, core=core, default=msg)
    assert outputs[0][0] == 'fail'

    outputs = _test_node('nodes/Switch', attr={
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

    outputs = _test_node('nodes/Switch', attr={
        'filter': {
            'type': 'expression',
            'value': 'len($.foo) is 3'
        }
    }, core=core, default=msg)
    assert outputs[0][0] == 'default'


def test_node_Exec(core):

    msg = Message()

    outputs = _test_node('nodes/Exec', attr={
        'command': {
            'type': 'string',
            'value': 'ping -n 1 www.google.fr'
        }
    }, core=core, default=msg)

    assert outputs[-1][0] == 'default'
    assert outputs[-1][1]['payload']['code'] == 0

    outputs = _test_node('nodes/Exec', attr={
        'command': {
            'type': 'string',
            'value': 'ping -n 4 www.google.fr'
        },
        'output': 'spawn'
    }, core=core, default=msg)

    assert outputs[-1][0] == 'default'
    assert outputs[-1][1]['payload']['code'] == 0


def test_node_Http_request(core):

    msg = Message()

    outputs = _test_node('nodes/HttpRequest', attr={
        'url': {
            'type': 'string',
            'value': 'http://www.google.fr'
        }
    }, core=core, default=msg)

    assert outputs[0][0] == 'default'
    assert outputs[0][1]['payload']['status_code'] == 200

