# coding: utf-8
import pytest
from ething.reg import *
from ething.Resource import *
from ething.File import File
import time


def test_extends(core):
    f = core.create('resources/File', {
        'name': 'file1.txt'
    })

    assert f.extends == ['resources/File', 'resources/Resource']


def test_attr_data_changed(core):
    class CDCCA(Resource):
        pass

    tac = core.create(CDCCA, {
        'name': 'toto',
    })

    with tac:
        dbg(tac)
        tac.data['foo'] = 'bar'
        assert 'data' in list_dirty_attr(tac)

    assert tac.data['foo'] == 'bar'


def test_attr_changed(core):

    attr_changed = set()
    attr_changed2 = set()

    @attr('cccaa', type=String(), default='', force_watch=True)
    @attr('cccab', type=String(), default='b')
    class CCCA(Resource):

        def on_attr_update(self, attr, new_value, old_value):
            super(CCCA, self).on_attr_update(attr, new_value, old_value)

            attr_changed.add(attr)

            if attr == 'cccaa' or attr == 'cccab':
                print('cccaa changed', new_value)
                attr_changed2.add(attr)


    @attr('cccba', type=String(), default='', force_watch=True)
    class CCCB(Resource):

        def on_attr_update(self, attr, new_value, old_value):
            super(CCCB, self).on_attr_update(attr, new_value, old_value)

            if attr == 'cccba':
                print('cccba changed', new_value)
                attr_changed2.add(attr)


    @attr('taca', type=String(), default='', force_watch=True)
    class TAC(CCCA, CCCB):
        def on_attr_update(self, attr, new_value, old_value):
            super(TAC, self).on_attr_update(attr, new_value, old_value)

            if attr == 'taca':
                print('taca changed', new_value)
                attr_changed2.add(attr)


    tac = core.create(TAC, {
        'name': 'toto',
    })

    with tac:
        tac.taca = 'v'
        tac.cccaa = 'w'
        tac.cccab = 'b'
        tac.cccba = 'w'

    if 'modifiedDate' in attr_changed:
        attr_changed.remove('modifiedDate')

    assert attr_changed == set(['taca', 'cccaa', 'cccba'])
    assert attr_changed2 == set(['taca', 'cccaa', 'cccba'])


def test_dynamic(core):

    @attr('cccaa', type=String(), default='')
    class TDCCCA(Resource):
        pass

    @attr('cccba', type=String(), default='')
    class TDCCCB(Resource):
        pass

    @attr('taca', type=String(), default='')
    @dynamic
    class TDTAC(Resource):
        pass


    c = create_dynamic_class(TDTAC, TDCCCA, TDCCCB)

    assert issubclass(c, TDTAC)
    assert issubclass(c, TDCCCA)
    assert issubclass(c, TDCCCB)

    ist = core.create(c, {
        'name': 'toto',
    })

    assert isinstance(ist, TDTAC)
    assert isinstance(ist, TDCCCA)
    assert isinstance(ist, TDCCCB)

    s = serialize(ist)

    ist2 = unserialize(Resource, s, context={'core': core})

    assert isinstance(ist, TDTAC)
    assert isinstance(ist, TDCCCA)
    assert isinstance(ist, TDCCCB)


def test_async_processing(core):

    glo = {
        'count': 0,
        'count2': 0
    }

    @attr('count2', type=Number(), default=0)
    @attr('count', type=Number(), default=0)
    class TAPA(Resource):

        @set_interval(1)
        def async_processing(self):
            self.count += 1
            glo['count'] += 1

        @process()
        def daemon_like_async_processing(self):
            while True:
                self.count2 += 1
                glo['count2'] += 1
                time.sleep(1)

    instance = core.create(TAPA, {
        'name': 'toto',
    })

    time.sleep(3)

    assert instance.count >= 2
    assert instance.count2 >= 2
    assert glo['count'] >= 2
    assert glo['count2'] >= 2

    instance.remove()

    count = glo['count']
    count2 = glo['count2']

    time.sleep(2)

    assert glo['count'] == count
    assert glo['count2'] == count2



