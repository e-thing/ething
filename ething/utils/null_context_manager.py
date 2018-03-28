
class NullContextManager(object):
  def __enter__(self):
    return None
  def __exit__(self, *args):
    pass
  def __nonzero__(self):
    return False
  def __bool__(self):
    return False

