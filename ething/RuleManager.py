# coding: utf-8

from .plugin import Plugin
from .Scheduler import Scheduler
from .Process import Process
import threading
import time


class RuleManager(Plugin):

    def load(self):
        self.process = RuleProcess(self.core)
        self.process.start()

    def unload(self):
        if hasattr(self, 'process'):
            self.process.stop()
            del self.process


class RuleProcess(Process):

    def __init__(self, core):
        super(RuleProcess, self).__init__('rule')

        self.core = core

        self._queue = []
        self._cache = {}

        self.scheduler = Scheduler()

        self.scheduler.setInterval(1, self.process)

        self._lock = threading.Lock()


    def main(self):
        self._queue = []
        self._cache = {}
        self._build_cache()

        self.core.signalDispatcher.bind(
            'ResourceCreated ResourceDeleted', self.onResourceCreatedOrDeleted)
        self.core.signalDispatcher.bind(
            'ResourceMetaUpdated', self.onResourceMetaUpdated)

        self.core.signalDispatcher.bind('*', self.dispatchSignal)

        while not self.stopped():
            time.sleep(0.5)
            self.scheduler.process()

        self.core.signalDispatcher.unbind(
            'ResourceCreated ResourceDeleted', self.onResourceCreatedOrDeleted)
        self.core.signalDispatcher.unbind(
            'ResourceMetaUpdated', self.onResourceMetaUpdated)

        self.core.signalDispatcher.unbind('*', self.dispatchSignal)

    def onResourceCreatedOrDeleted(self, signal):
        if signal['rType'] == 'Rule':
            self._build_cache()

    def onResourceMetaUpdated(self, signal):
        if signal['rType'] == 'Rule' and ( 'events' in signal['attributes'] or 'enabled' in signal['attributes'] or 'scheduler' in signal['attributes']):
            self._build_cache()

    def dispatchSignal(self, signal):
        with self._lock:
            self._queue.append(signal)

    def process(self):
        with self._lock:
            if len(self._queue) == 0:
                return  # no signal to process

            if self._cache:
                # no need to process signals when there is no rule registered

                if 'ResourceMetaUpdated' in self._cache:
                    # fuse ResourceMetaUpdated signals
                    f = 0
                    l = len(self._queue)
                    while l > 0:
                        l -= 1

                        signal = self._queue[l]
                        signal_type = type(signal).__name__
                        if signal_type == "ResourceMetaUpdated":
                            # merge with previous signal
                            i = 0
                            while i < l:
                                s = self._queue[i]
                                s_type = type(s).__name__
                                if s_type == "ResourceMetaUpdated" and signal['resource'] == s['resource']:
                                    # ok same signal describing the same resource -> merge the attributes
                                    signal['attributes'] = list(
                                        set(signal['attributes']).union(set(s['attributes'])))
                                    self._queue.pop(i)
                                    i -= 1
                                    l -= 1
                                    f += 1

                                i += 1

                    self.log.debug("signal fuse number %d" % f)

                for signal in self._queue:
                    signal_type = type(signal).__name__
                    for rule in self._cache.get(signal_type, []):
                        if rule.is_active:
                            if rule.signal_match(signal):
                                self.log.debug(
                                    "process rule %s from signal %s" % (rule, signal_type))
                                threading.Thread(target=self.process_signal, args=(signal, rule), name='rule').start()
                            # else:
                            #     rule.save() # done in signal_match

            self._queue = []

    def _build_cache(self):

        with self._lock:
            self.log.debug("rebuild rules cache")
            self._cache.clear()

            rules = self.core.find({
                'type': 'Rule',
                'enabled': True
            })

            for rule in rules:

                signals = set([event.signal.__name__ for event in rule.events])

                for signal in signals:
                    if signal not in self._cache:
                        self._cache[signal] = []

                    self._cache[signal].append(rule)

    def process_signal(self, signal, rule):
        rule.refresh(keepDirtyFields = True)  # need to be refreshed because some attributes may have changed since the last time the _cache has been updated
        rule.run(signal)
