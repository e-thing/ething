# coding: utf-8
import pytest
from ething.core.rule import event, action


def test_rule(core):

    rule = core.create('resources/Rule', {
        'name': 'myrule',
        'events': [
            event.CustomEvent({
                'name': 'my_event'
            })
        ],
        'actions': [
            action.Wait.Wait({
                'duration': 200
            })
        ]
    })

    assert rule

    signal = event.Custom('my_event')

    rule.trigger(signal)

    assert rule.execution_count == 1


def test_HttpRequest():
    signal = event.Custom('my_event')

    req_action = action.HttpRequest.HttpRequest({
        'url': 'http://www.google.fr'
    })

    req_action.run(signal)




