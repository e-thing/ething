# coding: utf-8
import pytest
from ething.core.entity import *


def test_cls():

  @attr('foo', type=String(), default='hello')
  @attr('bar', type=Number())
  class A(Entity):
    pass

  a = A({
    'bar': 12
  })

  assert a.foo == 'hello'
  assert a.bar == 12

  with pytest.raises(AttributeError):
    a = A()


def test_computed():
  @attr('foo', type=String(), default='hello')
  class B(Entity):

    @attr()
    def bar(self):
      return 12

  a = B()

  assert a.foo == 'hello'
  assert a.bar == 12


def test_schema():
  @attr('foo', type=String(), default='hello')
  class C(Entity):

    @attr()
    def bar(self):
      return 12

  print(C.toSchema())