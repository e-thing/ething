from scapy.sendrecv import sr1
from scapy.layers.inet import IP, ICMP

def pingable(cls):
	setattr(cls, 'ping', ping)
	return cls

def ping(self, timeout = 1):
	
	host = self.host
	
	try:
		result = sr1(IP(dst=host)/ICMP(), timeout = timeout, verbose = False)
	except:
		result = False
	
	online = bool(result)
	
	self.setConnectState(online)
	
	return result





if __name__ == '__main__':
	
	
	@pingable
	class Test(object):
		
		def __init__(self):
			self.host = 'example.com'
		
		def setConnectState(self, online):
			print 'set online =', online
	
	t = Test()
	t.ping()
	