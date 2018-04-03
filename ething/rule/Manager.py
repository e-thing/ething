
from Rule import Rule


class Manager(object):
    
    def __init__(self, core):
        self.core = core
        self.db = core.db
        self.log = core.log
        self.taskmanager = core.taskManager
        
        self._queue = []
        
        core.scheduler.tick(self.process)
    
    
    def dispatchSignal (self, signal):
        self._queue.append(signal)
    
    
    def process(self):
        
        if len(self._queue) == 0:
            return # no signal to process
        
        # fuse ResourceMetaUpdated signals 
        f = 0;
        l = len(self._queue)
        while l>0:
            l -= 1
            
            signal = self._queue[l]
            if signal.name == "ResourceMetaUpdated":
                # merge with previous signal
                i = 0
                while i<l:
                    s = self._queue[i]
                    if s.name == "ResourceMetaUpdated" and signal['resource'] == s['resource']:
                        # ok same signal describing the same resource -> merge the attributes
                        signal['attributes'] = list(set(signal['attributes']).union(set(s['attributes'])))
                        self._queue.pop(i)
                        i -= 1
                        l -= 1
                        f += 1
                    
                    i+=1
        
        self.log.debug("signal fuse number %d" % f)
        
        for signal in self._queue:
            self.taskmanager.run(self.process_signal, args=(signal,), name = 'rule')
        
        self._queue = []
    
    
    def process_signal(self, signal):
        
        # get all the rules enabled and with the correct type/name
        query = {
            'events.type' : signal.name,
            'enabled' : True
        }
        
        # get all the rules of the event type
        rules = self.core.findRules(query)
        
        for rule in rules:
            rule.trigger(signal)
    
    
    