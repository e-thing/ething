# coding: utf-8




class RuleManager(object):
    
    def __init__(self, core):
        self.core = core
        self.db = core.db
        self.log = core.log
        self.taskmanager = core.taskManager
        
        self._queue = []
        
        core.scheduler.tick(self.process)
        
        self._cache = {}
        
        self.core.signalManager.bind('ResourceCreated ResourceMetaUpdated ResourceDeleted', self.onResourceChanged)
    
    def destroy(self):
        self.core.signalManager.unbind('ResourceCreated ResourceMetaUpdated ResourceDeleted', self.onResourceChanged);
    
    
    def onResourceCreated(self, signal):
        if signal['rType'] == 'Rule' :
            self._empty_cache()
    
    
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
            signal_type = type(signal).__name__
            if signal_type == "ResourceMetaUpdated":
                # merge with previous signal
                i = 0
                while i<l:
                    s = self._queue[i]
                    s_type = type(s).__name__
                    if s_type == "ResourceMetaUpdated" and signal['resource'] == s['resource']:
                        # ok same signal describing the same resource -> merge the attributes
                        signal['attributes'] = list(set(signal['attributes']).union(set(s['attributes'])))
                        self._queue.pop(i)
                        i -= 1
                        l -= 1
                        f += 1
                    
                    i+=1
        
        self.log.debug("signal fuse number %d" % f)
        
        for signal in self._queue:
            signal_type = type(signal).__name__
            
            if self._cache.get(signal_type) == []:
                return
            
            self.taskmanager.run(self.process_signal, args=(signal,), name = 'rule')
        
        self._queue = []
    
    
    def _empty_cache(self):
        self._cache.clear()
    
    def _get(self, signal_type):
        
        if signal_type not in self._cache:
            
            # get all the rules and with the correct type/name
            query = {
                'type': 'Rule',
                'event.signal' : signal_type,
            }
            
            # get all the rules of the event type
            self._cache[signal_type] = self.core.find(query)
            
        
        return self._cache.get(signal_type, [])
    
    def process_signal(self, signal):
        
        signal_type = type(signal).__name__
        
        # get all the rules of the event type
        rules = self.core.find(query)
        
        for rule in self._get(signal_type):
            if rule.enabled:
                rule.run(signal)
    
    
    