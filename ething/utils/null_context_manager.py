# coding: utf-8
from builtins import object

class NullContextManager(object):
  def __enter__(self):
    return None
  
  def __exit__(self, *args):
    pass
  
  def __bool__(self):
    return False

