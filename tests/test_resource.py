# coding: utf-8
import pytest
from ething.core.reg import *
from ething.core.Resource import Resource
from ething.core.File import File


def test_extends(core):
    f = core.create('resources/File', {
        'name': 'file1.txt'
    })

    assert f.extends == ['resources/File', 'resources/Resource']


def test_attr_changed(core):

    attr_changed = set()
    attr_changed2 = set()

    @attr('cccaa', type=String(), default='', force_watch=True)
    @attr('cccab', type=String(), default='b')
    class CCCA(Resource):

        def on_attr_update(self, attr, new_value, old_value):
            super(CCCA, self).on_attr_update(attr, new_value, old_value)

            attr_changed.add(attr)

            if attr == 'cccaa':
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

    assert attr_changed == set(['taca', 'cccaa', 'cccba', 'modifiedDate'])
    assert attr_changed2 == set(['taca', 'cccaa', 'cccba'])




