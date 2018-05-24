# coding: utf-8
import pytest
from ething.meta import *
from future.utils import with_metaclass


def test_meta():

    # static interface
    class InterfaceA(iface):

        @method
        def method_a_1(self):
            pass

        @method
        def method_a_2(self):
            pass

    # static interface
    class InterfaceB(iface):

        @method
        def method_b_1(self):
            pass

        @method
        def method_b_2(self):
            pass

    # create a new interface with static inheritance of interface InterfaceA + dyn inheritance of InterfaceB

    class DynInterface(with_metaclass(MetaInterface, InterfaceA)):
        pass

    d = DynInterface()

    assert hasattr(d, 'method_a_1')
    assert hasattr(d, 'method_a_2')

    # make d inherit from InterfaceB
    interface.inherit(d, InterfaceB)

    assert hasattr(d, 'method_b_1')
    assert hasattr(d, 'method_b_2')

    # remove all dynamic inheritance
    interface.clear(d)

    assert hasattr(d, 'method_a_1')
    assert hasattr(d, 'method_a_2')
    assert not hasattr(d, 'method_b_1')
    assert not hasattr(d, 'method_b_2')
