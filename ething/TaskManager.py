from multiprocessing import Process
import time




class Task(object):
    
    def __init__(self, manager, func, args = (), kwargs = {}, name = None):
        self._manager = manager
        self._start_time = None
        self._end_time = None
        self._exit_code = None
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._p = None
        self.log = manager.log
        self._name = name if name is not None else (func.__name__ or 'anonymous')
    
    @property
    def manager(self):
        return self._manager
    
    @property
    def name(self):
        return self._name
    
    @property
    def start_time(self):
        return self._start_time
    
    @property
    def end_time(self):
        return self._end_time
    
    @property
    def duration(self):
        return (self._end_time - self._start_time) if self._end_time is not None else None
    
    @property
    def exit_code(self):
        return self._p.exitcode if self._p is not None else None
    
    @property
    def pid(self):
        return self._p.pid if self._p is not None else None
    
    @property
    def is_started (self):
        return self._p is not None
    
    @property
    def is_running (self):
        return self._p is not None and self._p.is_alive()
    
    # must be called by the manager
    def start(self):
        self.log.debug("start task '%s'" % self.name)
        self._start_time = time.time()
        self._p = Process(target=self._func, args=self._args, kwargs=self._kwargs)
        self._p.start()
    
    
    def stop(self):
        if self.is_running:
            self.log.debug("stop task '%s', pid=%d" % (self.name, self.pid))
            self._p.terminate()
            self._p.join()
        
        if self._end_time is None and self._p:
            self._end_time = time.time()
    
    def loop(self):
        if self._end_time is None and self._p is not None and not self._p.is_alive():
            self._end_time = time.time()
            self.log.debug("task '%s' ended, exit_code=%d , duration=%f" % (self.name, self.exit_code, self.duration))
    
    
    
    

class TaskManager(object):
    
    
    def __init__(self, core, max_running_tasks = 12):
        self.core = core
        self.log = core.log
        
        self._max_running_tasks = max_running_tasks
        self._tasks = []
    
    @property
    def max_running_tasks(self):
        return self._max_running_tasks
    
    @property
    def tasks(self):
        return self._tasks
    
    
    def run(self, task, args = (), kwargs = {}, name = None):
        
        if callable(task):
            task = Task(self, task, args=args, kwargs=kwargs, name=name)
        else:
            raise ValueError("task must be callable")
        
        self._tasks.append(task)
        
        return task
    
    def terminate(self):
        for task in self._tasks:
            task.stop()
    
    
    def get_task_by_name(self, name):
        for task in self.tasks:
            if task.name == name:
                return task
    
    
    def loop(self):
        
        now = time.time()
        pending_tasks = []
        running_tasks_count = 0
        i = len(self._tasks)
        while i > 0:
            i -= 1
            
            task = self._tasks[i]
            
            task.loop()
            
            if not task.is_started:
                pending_tasks.append(task)
            else:
                if task.is_running:
                    running_tasks_count += 1
                else:
                    # the task is finished
                    if now - task.end_time > 60:
                        # remove from the queue
                        self._tasks.pop(i)
            
        for task in pending_tasks:
            if running_tasks_count < self.max_running_tasks:
                running_tasks_count += 1
                task.start()
            
    
    def print_info(self):
        
        lines = []
        
        lines.append('name            | status')
        lines.append('------------------------------------------------------------')
        
        for task in self.tasks:
            
            status = '?'
            
            if not task.is_started:
                status = 'pending'
            else:
                if task.is_running:
                    status = 'running, pid=%d, duration=%f sec' % (task.pid, time.time() - task.start_time)
                else:
                    status = 'finished, exit_code=%d, duration=%f sec' % (task.exit_code, task.duration)
            
            lines.append('%-16s| %s' % (task.name, status))
        
        lines.append('------------------------------------------------------------')
        
        for line in lines:
            self.log.info(line)
        
        return "\n".join(lines)
    

if __name__ == '__main__':
    
    import logging
    
    logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    class Core(object):
        log = logger
    
    
    manager = TaskManager(Core(), max_running_tasks = 2)
    
    def sleep(sec):
        print 'start sleeping for %d sec' % sec
        time.sleep(sec)
        print 'stop sleeping for %d sec' % sec
    
    for i in range(0,4):
        manager.run(sleep, args = (i+1, ), name = ('task %d'%i))
    
    
    try:
        while True:
            time.sleep(0.1)
            manager.loop()
    except KeyboardInterrupt:
        manager.print_info()
        manager.terminate()
        manager.print_info()
    
    
    
    
    
    
    
    
    