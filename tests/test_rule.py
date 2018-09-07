# coding: utf-8
import pytest
from ething.core.Rule import event, action


def test_rule(core):

    rule = core.create('resources/Rule', {
        'name': 'myrule',
        'events': [
            event.Custom.CustomEvent({
                'name': 'my_event'
            })
        ],
        'actions': [
            action.Notify.Notify({
                'message': 'hello'
            })
        ]
    })

    assert rule

    signal = event.Custom.Custom('my_event')

    rule.trigger(signal)

    assert rule.execution_count == 1
