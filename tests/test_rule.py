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

    context = {
        'ething': core
    }

    signal = FileDataModified(f)

    evt0 = FileDataModifiedEvent({
        'resource': f.id
    }, context)

    assert evt0.filter(signal, core, None)

    evt1 = FileDataModifiedEvent({
        'resource': f1.id
    }, context)

    assert not evt1.filter(signal, core, None)

    evt2 = FileDataModifiedEvent({
        'resource': [f.id]
    }, context)

    assert evt2.filter(signal, core, None)

    evt3 = FileDataModifiedEvent({
        'resource': 'name == "file1.txt"'
    }, context)

    assert evt3.filter(signal, core, None)

    with pytest.raises(Exception) as excinfo:
        evt4 = FileDataModifiedEvent({
            'resource': '0123456' # invalid id
        }, context)

        assert 'does not exist' in str(excinfo.value)


def test_event_ResourceFilter(core):
    f = core.create('resources/File', {
        'name': 'file1.txt'
    })

    t = core.create('resources/Table', {
        'name': 'table0'
    })

    context = {
        'ething': core
    }

    rf = event.ResourceFilter(must_throw=FileDataModified)

    rf.validate(f.id, context)

    rf.validate([f.id], context)

    rf.validate("name=='toto'", context)

    with pytest.raises(Exception) as excinfo:
        rf.validate(t.id, context)
        assert 'does not throw the signal' in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        rf.validate([t.id, f.id], context)
        assert 'does not throw the signal' in str(excinfo.value)

    rf2 = event.ResourceFilter(onlyTypes=('resources/File',))

    rf2.validate(f.id, context)

    with pytest.raises(Exception) as excinfo:
        rf2.validate(t.id, context)
        assert 'must be one of the following types' in str(excinfo.value)


def test_condition_ResourceMatch(core):

    f = core.create('resources/File', {
        'name': 'file1.txt'
    })

    context = {
        'ething': core
    }

    signal = event.Custom('my_event')

    c1 = condition.ResourceMatch.ResourceMatch({
        'resource': f.id,
        'expression': 'name == "file1.txt"'
    }, context)

    assert c1.test(signal, core, None)

    c2 = condition.ResourceMatch.ResourceMatch({
        'resource': f.id,
        'expression': 'name == "toto.txt"'
    }, context)

    assert not c2.test(signal, core, None)


def test_action_HttpRequest():
    signal = event.Custom('my_event')

    req_action = action.HttpRequest.HttpRequest({
        'url': 'http://www.google.fr'
    })

    req_action.run(signal, None, None)




