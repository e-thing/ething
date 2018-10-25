# coding: utf-8
import pytest
from ething.core.rule import event, condition, action
from ething.core.File import FileDataModifiedEvent, FileDataModified


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


def test_event_ResourceEvent(core):
    f = core.create('resources/File', {
        'name': 'file1.txt'
    })

    f1 = core.create('resources/File', {
        'name': 'file2.txt'
    })

    assert core.get(f.id)

    signal = FileDataModified(f)

    evt0 = FileDataModifiedEvent({
        'resource': f.id
    })

    assert evt0.filter(signal, core, None)

    evt1 = FileDataModifiedEvent({
        'resource': f1.id
    })

    assert not evt1.filter(signal, core, None)

    evt2 = FileDataModifiedEvent({
        'resource': [f.id]
    })

    assert evt2.filter(signal, core, None)

    evt2 = FileDataModifiedEvent({
        'resource': 'name == "file1.txt"'
    })

    assert evt2.filter(signal, core, None)


def test_condition_ResourceMatch(core):

    f = core.create('resources/File', {
        'name': 'file1.txt'
    })

    signal = event.Custom('my_event')

    c1 = condition.ResourceMatch.ResourceMatch({
        'resource': f.id,
        'expression': 'name == "file1.txt"'
    })

    assert c1.test(signal, core, None)

    c2 = condition.ResourceMatch.ResourceMatch({
        'resource': f.id,
        'expression': 'name == "toto.txt"'
    })

    assert not c2.test(signal, core, None)


def test_action_HttpRequest():
    signal = event.Custom('my_event')

    req_action = action.HttpRequest.HttpRequest({
        'url': 'http://www.google.fr'
    })

    req_action.run(signal, None, None)




