from multiprocessing import Process
import os
import signal

    

class WebServer(object):
    
    
    def __init__(self, core):
        
        self.core = core
        self.p = None
    
    @property
    def is_started (self):
        return self.p is not None and self.p.is_alive()
    
    def __proc(self):
        
        # remove any signal handlers set by the parents
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        
        self.core.log.info("webserver process started, pid = %d" % os.getpid() )
        
        try:
            from ething.webserver.server import run
            
            run(self.core)
        except:
            self.core.log.exception("webserver stopped")
        
        self.core.log.info("webserver process ended")
    
    def start(self):
        #run webserver in another process
        self.p = Process(target=self.__proc, args=())
        self.p.daemon = True
        self.p.start()
    
    def stop(self):
        if self.is_started:
            self.core.log.info("stopping webserver")
            self.p.terminate()
            self.p.join()
            self.core.log.info("webserver stopped")
            self.p = None
        
        
        