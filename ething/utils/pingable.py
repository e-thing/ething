from scapy.sendrecv import sr1
from scapy.layers.inet import IP, ICMP


def pingable(attr = 'host'):
    def d(cls):
        def f(self, *args, **kwargs):
            
            host = getattr(self, attr, None)
            online = False
            
            if host:
                online = ping(host, *args, **kwargs)
            
            self.setConnectState(online)
            
            return online
        
        setattr(cls, 'ping', f)
        return cls
    return d

def ping(host, timeout = 1):
    
    try:
        result = sr1(IP(dst=host)/ICMP(), timeout = timeout, verbose = False)
    except:
        result = False
    
    return bool(result)





if __name__ == '__main__':
    
    
    @pingable
    class Test(object):
        
        def __init__(self):
            self.host = 'example.com'
        
        def setConnectState(self, online):
            print 'set online =', online
    
    t = Test()
    t.ping()
    