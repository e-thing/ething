# coding: utf-8

from ..plugin import Plugin
from ..Process import Process
from .Rule import Rule
import threading


class RuleManager(Plugin):

    def load(self):
        self._queue = []
        self._cache = {}
        self._lock = threading.Lock()

    def setup(self):
        self._build_cache()

        self.core.signalDispatcher.bind(
            'ResourceCreated ResourceDeleted', self.onResourceCreatedOrDeleted)
        self.core.signalDispatcher.bind(
            'ResourceUpdated', self.onResourceUpdated)

        self.core.signalDispatcher.bind('*', self.dispatchSignal)

        self.core.scheduler.setInterval(1, self.process)

    def onResourceCreatedOrDeleted(self, signal):
        if isinstance(signal.resource, Rule):
            self._build_cache()

    def onResourceUpdated(self, signal):
        if isinstance(signal.resource, Rule) and ( 'events' in signal['attributes'] or 'enabled' in signal['attributes'] ):
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

                if 'ResourceUpdated' in self._cache:
                    # fuse ResourceUpdated signals
                    f = 0
                    l = len(self._queue)
                    while l > 0:
                        l -= 1

                        signal = self._queue[l]
                        signal_type = type(signal).__name__
                        if signal_type == "ResourceUpdated":
                            # merge with previous signal
                            i = 0
                            while i < l:
                                s = self._queue[i]
                                s_type = type(s).__name__
                                if s_type == "ResourceUpdated" and signal.resource == s.resource:
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
                                Process(target=self.process_signal, args=(signal, rule), name='rule').start()
                            # else:
                            #     rule.save() # done in signal_match

            self._queue = []

    def _build_cache(self):

        with self._lock:
            self.log.debug("rebuild rules cache")
            self._cache.clear()

            rules = self.core.find(lambda r: r.isTypeof('resources/Rule') and r.enabled)

            for rule in rules:

                signals = set([event.signal.__name__ for event in rule.events])

                for signal in signals:
                    if signal not in self._cache:
                        self._cache[signal] = []

                    self._cache[signal].append(rule)

    def process_signal(self, signal, rule):
        if rule.condition_match(signal):
            rule.run(signal)
