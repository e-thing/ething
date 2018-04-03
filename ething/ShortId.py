

from shortid import ShortId as ShortIdlib
import re


class ShortId(object):
    
    sid = None
    
    # length of the identifier (must be between 7 and 14)
    length = 7
    # alphabet to use when generating the identifier (must be 64 characters long)
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-'
    
    
    @staticmethod
    def generate():
        
        if ShortId.sid is None:
            ShortId.sid = ShortIdlib()
        
        return ShortId.sid.generate()[:ShortId.length]
    
    
    @staticmethod
    def validate (id):
        if isinstance(id, basestring) and len(id)==ShortId.length:
            match = re.match("^["+ShortId.alphabet+"]*$", id)
            return match is not None
        return False
    
    
if __name__ == '__main__':
    
    print ShortId.validate('1234567')
    print ShortId.validate('123456')
    print ShortId.validate('123?f56')
    
    ids = []
    for i in range(0,10000):
        ids.append(ShortId.generate())
    
    
    import collections
    print [item for item, count in collections.Counter(ids).items() if count > 1]
    
