# coding: utf-8
import pytest
from ething.core.reg import *
import json
import abc


def test_glob():
    @attr('id', type='int')
    @attr('foo', type=String(allow_empty=False), default="bar")
    class AG(Entity):
        pass

    a = AG({
        'id': 2
    })

    assert a.foo == 'bar'

    assert is_dirty(a) is False

    a.foo = 'toot'
    assert is_dirty(a) is True
    assert a.foo == 'toot'

    with pytest.raises(ValueError):
        a.foo = ''

    assert a.foo == 'toot'


def test_transaction():
    @attr('id', type='int')
    @attr('foo', type=String(allow_empty=False), default="bar")
    class AT(Entity):
        def __init__(self, *args):
            super(AT, self).__init__(*args)
            self.t_cnt = 0
            self.watch_map = {}

        def __watch__(self, attr, val, old_val):
            if attr.name not in self.watch_map:
                self.watch_map[attr.name] = 0
            self.watch_map[attr.name] += 1

        def __transaction_end__(self):
            self.t_cnt += 1

    a = AT({
        'id': 2
    })

    assert a.foo == 'bar'
    assert a.t_cnt == 0

    with a:
        a.foo = 'toto'
        assert a.t_cnt == 0
        a.foo = 'titi'
        assert a.t_cnt == 0

    assert a.t_cnt == 1
    assert a.foo == 'titi'


def test_computed_attr():

    @attr('id', type='int')
    @attr('foo', type=String(allow_empty=False), default="bar")
    class AC(Entity):

        @attr()
        def computed_attr(self):
            return type(self).__name__

        @attr()
        @staticmethod
        def computed_attr_static():
            return 'hello'

        @attr()
        @classmethod
        def computed_attr_class(cls):
            return cls.__name__

    assert AC.foo == 'bar'
    assert AC.computed_attr_static == 'hello'
    assert AC.computed_attr_class == AC.__name__

    assert len(list_registered_attr(AC)) == 5

    a0 = create(AC, {
        'id': 2
    })

    assert a0.id == 2
    assert a0.foo == 'bar'

    assert a0.computed_attr == AC.__name__

    @attr('foo', default="bar_mod")
    @attr('b_attr', type=String(allow_empty=False), default="tuut")
    class BC(AC):

        def meth_foo(self, suffix=''):
            return 'res_overloaded' + suffix

    assert BC.computed_attr_class == BC.__name__


def test_methode():
    @attr('id', type='int')
    @attr('foo', type=String(allow_empty=False), default="bar")
    class AM(Entity):

        @method
        def meth_foo(self):
            return 'res'

        @method
        @staticmethod
        def meth_foo_static():
            return 'res_static'

        @method
        @classmethod
        def meth_foo_class(cls):
            return 'res_class'

        @method.arg('a', type='number')
        def meth_add(self, a, b=0):
            return a + b

    a = AM({
        'id': 2
    })

    assert AM.meth_foo_static() == 'res_static'
    assert AM.meth_foo_class() == 'res_class'

    assert a.meth_foo() == 'res'

    assert a.meth_add(2, 4) == 6

    assert len(list_registered_methods(AM)) == 4

    @attr('foo', default="bar_mod")
    @attr('b_attr', type=String(allow_empty=False), default="tuut")
    class BM(AM):

        def meth_foo(self, suffix=''):
            return 'res_overloaded' + suffix

    b = BM({
        "id": 4
    })

    assert b.meth_foo() == 'res_overloaded'

    with pytest.raises(ValueError):
        b.meth_foo(2)


def test_nested():
    @attr('id', type='int')
    class D(Entity):
        pass

    @attr('nested', type=D)
    @attr('id', type='int')
    class E(Entity):
        pass

    print(json.dumps(build_schema(E), sort_keys=True, indent=2))

    e = E({
        'id': 1,
        'nested': D({
            'id': 2
        })
    })

    print(json.dumps(toJson(e), sort_keys=True, indent=2))

    assert is_dirty(e) is False
    assert is_dirty(e.nested) is False
    assert len(list_dirty_attr(e)) == 0

    assert type(e.nested) is D
    assert e.nested.id == 2

    e.nested.id = 3
    assert is_dirty(e) is True
    assert is_dirty(e.nested) is True
    assert len(list_dirty_attr(e)) == 1 and list_dirty_attr(e)[0].name == 'nested'
    assert len(list_dirty_attr(e.nested)) == 1 and list_dirty_attr(e.nested)[0].name == 'id'

    clean(e)
    assert is_dirty(e) is False
    assert is_dirty(e.nested) is False

    # nested array

    @attr('nested', type=Array(D), default=lambda _: [D({'id': 0})])
    @attr('id', type='int')
    class F(Entity):
        pass

    f = F({
        'id': 5
    })

    print(json.dumps(toJson(f), sort_keys=True, indent=2))

    assert is_dirty(f) is False
    assert is_dirty(f.nested) is False
    assert is_dirty(f.nested[0]) is False

    f.nested[0].id = 8
    assert is_dirty(f) is True
    assert is_dirty(f.nested) is True
    assert is_dirty(f.nested[0]) is True
    print(json.dumps(toJson(f), sort_keys=True, indent=2))

    clean(f)
    assert is_dirty(f) is False
    assert is_dirty(f.nested) is False
    assert is_dirty(f.nested[0]) is False


def test_not_entity():
    @attr('id', type='int')
    class C(object):
        pass

    c = C()

    c.id = 45
    assert c.id == 45

    c_copy = unserialize(C, serialize(c))

    assert serialize(c) == serialize(c_copy)

    # nested not entity class

    @attr('name', type='string', default="toto")
    class CC(object):
        pass

    @attr('nested', type=CC)
    @attr('id', type='int')
    class CP(object):
        pass

    cp = CP()
    cp.id = 5
    cp.nested = CC()
    assert cp.nested.name == 'toto'


def test_internal_data():
    a = Attribute('foo')
    b = Attribute('bar')
    d = {}
    d[a] = 'foo_val'
    d[b] = 'bar_val'

    di = InternalData(d)

    assert di['foo'] == 'foo_val'
    assert di['bar'] == 'bar_val'


def test_discriminate():
    @discriminate()
    @attr('name', type="string")
    @uid()
    class HBase(Entity):
        def print_name(self):
            print(type(self).__name__, self.name)

    class HA(HBase):
        pass

    ha = HA({'name': 'ha'})

    s_ha = serialize(ha)
    assert s_ha['type'] == 'HA'
    ha_copy = unserialize(HBase, s_ha)

    assert ha_copy.type == 'HA'

    assert type(ha_copy) is HA


def test_context():
    class I(Entity):
        pass

    i = I(context={
        'foo': 'bar'
    })

    assert i.foo == 'bar'

