

class SignalManager(object):
    
    
    
    def __init__(self, core):
        self.core = core
        self.log = core.log
        self.handlers = {}
        self.dispatchers = []
        
        self.addDispatcher(self.default_dispatcher)
        
        self.core.rpc.register('signal', self.dispatch)
    
    def default_dispatcher (self, signal):
        event_type = signal.name
        
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(signal)
                except Exception as e:
                    self.log.exception("Error calling signal handler with signal: %s handler: %s" % (str(signal), handler))
    
    def dispatch (self, signal):
        
        self.log.debug("dispatchSignal : %s" % str(signal))
        
        for dispatcher in self.dispatchers:
            try:
                dispatcher(signal)
            except Exception as e:
                self.log.exception("Error calling signal dispatcher with signal: %s dispatcher: %s" % (str(signal), dispatcher))
    
    
    def bind (self, event_type, handler):
        """Adds an event listener for event name"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
    
    
    def unbind (self, event_type, handler):
        """removes previously added event listener"""
        if event_type in self.handlers:
            try:
                self.handlers[event_type].remove(handler)
            except KeyError:
                pass
        
    def addDispatcher(self, dispatcher):
        self.dispatchers.append(dispatcher)
    
    def removeDispatcher(self, dispatcher):
        if dispatcher in self.dispatchers:
            self.dispatchers.remove(dispatcher)
    
    
    
    

