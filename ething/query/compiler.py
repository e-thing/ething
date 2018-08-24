# coding: utf-8

class Compiler (object):
  
  def _not_(self, a):
    raise NotImplementedError()
  
  def _and_(self, a, b):
    raise NotImplementedError()
  
  def _or_(self, a, b):
    raise NotImplementedError()
  
  def _eq_(self, field, value):
    raise NotImplementedError()
  
  def _ne_(self, field, value):
    raise NotImplementedError()
  
  def _gt_(self, field, value):
    raise NotImplementedError()
  
  def _lt_(self, field, value):
    raise NotImplementedError()
  
  def _ge_(self, field, value):
    raise NotImplementedError()
  
  def _le_(self, field, value):
    raise NotImplementedError()

  def _exists_(self, field):
    raise NotImplementedError()
  
  def _is_(self, field, value):
    raise NotImplementedError()
  
  def _has_(self, field, value):
    raise NotImplementedError()
  
  def _match_(self, field, value):
    raise NotImplementedError()


