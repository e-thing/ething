


import re

class Stream(object):
    
    
    def __init__ (self, content = None):
        self.index = 0
        self.index_last = 0
        if isinstance(content, basestring):
            self.content = content
        else:
            self.content = ''
    
    
    def currentIndex (self):
        return self.index
    
    
    def previousIndex (self):
        return self.index_last
    
    
    def walk (self, numberOfChar):
        if numberOfChar>0:
            length = len(self.content)
            if numberOfChar<length:
                self.content = self.content[numberOfChar:]
            else:
                numberOfChar = length
                self.content = ''
            
        
        self.index_last = self.index
        self.index += numberOfChar
        return numberOfChar
    
    
    def read (self, a):
        if isinstance(a, int) and a>0:
            # read n characters
            o = self.content[:a]
            self.walk(len(o))
            return o
        
        elif isinstance(a, basestring):
            # return the first match
            m = re.search(a, self.content)
            if m is not None:
                o = m.group(0)
                self.walk(m.start(0)+len(o))
                return o
            else:
                self.walk(0);# just for updating the index_last property
        
        return None
    
    
    def match (self, regex):
        m = re.search(regex, self.content)
        return bool(m)
    
    
    def skipSpace (self):
        return self.read('^\s*')
    
    
    def readWord (self):
        return self.read('[^\s]+')
    
    
    def length (self):
        return len(self.content)
    
    
    def __str__ (self):
        return self.content
    



