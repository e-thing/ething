# coding: utf-8

import time
import datetime


class Scheduler(object):
    
    
    def __init__(self, core):
        self.core = core
        self.log = core.log
        self.tasks = []
    
    def tick (self, callback):
        if callable(callback):
            self.tasks.append({
                'type' : 'tick',
                'callback' : callback
            })
            return True
        
        return False
    
    def setInterval (self, interval, callback, startInSec = 0):
        if callable(callback) and interval > 0:
            self.tasks.append({
                'type' : 'interval',
                'interval' : interval,
                'callback' : callback,
                'startIn' : startInSec,
                't0' : time.time(),
                'running' : False
            })
            return True
        
        return False
    
    
    def delay (self, delay, callback):
        if callable(callback) and delay > 0:
            self.tasks.append({
                'type' : 'delay',
                'delay' : delay,
                'callback' : callback,
                't0' : time.time()
            })
            return True
        
        return False
    
    
    def at (self, callback, hour = '*', min = 0):
        if callable(callback):
            self.tasks.append({
                'type' : 'at',
                'hour' : hour,
                'min' : min,
                'callback' : callback,
                't0' : time.time()
            })
            return True
        
        return False
    
    
    
    def run (self, task):
        task['lastRun'] = time.time()
        if 'executedCount' not in task:
            task['executedCount'] = 0
        task['executedCount'] += 1
        try:
            task['callback']()
        except:
            self.log.exception('[scheduler] exception in task "%s"' % task['callback'].__name__)
    
    
    
    def update (self):
        i=0
        while i < len(self.tasks):
            task = self.tasks[i]
            
            now = time.time()
            type = task['type']
            
            if type == 'tick':
                self.run(task)
                
            elif type == 'interval':
                if task['running']:
                    if (now - task['lastRun']) >= task['interval']:
                        self.run(task)
                    
                else:
                    if (now - task['t0']) >= task['startIn']:
                        task['running'] = True
                        self.run(task)
            
            elif type == 'delay':
                
                if (now - task['t0']) >= task['delay']:
                    self.run(task)
                    self.tasks.remove(task)
                    i-=1
            
            elif type == 'at':
                
                nowd = datetime.datetime.utcnow()
                
                if nowd.second<5 and (task['hour']=='*' or task['hour']==nowd.hour) and (task['min']=='*' or task['min']==nowd.minute) and ( ('lastRun' not in task) or (now - task['lastRun']) >= 55 ):
                    self.run(task)
            
            i+=1


