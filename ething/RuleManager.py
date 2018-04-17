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
        
        self._build_cache()
        
        self.core.signalManager.bind('ResourceCreated ResourceDeleted', self.onResourceCreatedOrDeleted)
        self.core.signalManager.bind('ResourceMetaUpdated', self.onResourceMetaUpdated)
        
        self.core.signalManager.addDispatcher(self.dispatchSignal)
    
    
    def destroy(self):
        self.core.signalManager.unbind('ResourceCreated ResourceDeleted', self.onResourceCreatedOrDeleted)
        self.core.signalManager.unbind('ResourceMetaUpdated', self.onResourceMetaUpdated)
        self.core.signalManager.removeDispatcher(self.dispatchSignal)
        self._cache.clear()
        self._queue = []
    
    
    def onResourceCreatedOrDeleted(self, signal):
        if signal['rType'] == 'Rule' :
            self._build_cache()
    
    def onResourceMetaUpdated(self, signal):
        if signal['rType'] == 'Rule' and 'event' in signal['attributes'] :
            self._build_cache()
            
    
    def dispatchSignal (self, signal):
        self._queue.append(signal)
    
    
    def process(self):
        
        if len(self._queue) == 0:
            return # no signal to process
        
        if self._cache:
            # no need to process signals when there is no rule registered
            
            if 'ResourceMetaUpdated' in self._cache:
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
                
                for rule in self._cache.get(signal_type, []):
                    if rule.event.filter(signal):
                        self.log.debug("process rule %s from signal %s" % (rule, signal_type))
                        self.taskmanager.run(self.process_signal, args=(signal,rule), name = 'rule')
        
        self._queue = []
    
    def _build_cache(self):
        self._cache.clear()
        
        rules = self.core.find({
            'type': 'Rule',
            'enabled': True
        })
        
        for rule in rules:
            signal = rule.event.signal
            
            if signal not in self._cache:
                self._cache[signal] = []
            
            self._cache[signal].append(rule)
    
    
    def process_signal(self, signal, rule):
        rule.refresh() # need to be refreshed because some attributes may have changed since the last time the _cache has been updated
        rule.run(signal)
    
    
    