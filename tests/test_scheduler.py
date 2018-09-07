# coding: utf-8
import pytest
from ething.core.Scheduler import Scheduler
import time


interval_counter = 0

def test_taskmanager():
    global interval_counter

    interval_counter = 0

    scheduler = Scheduler()

    def increase():
        global interval_counter
        interval_counter = interval_counter + 1

    scheduler.setInterval(0.5, increase)

    tf = time.time() + 3.2
    while time.time() < tf:
        scheduler.process()
        time.sleep(0.2)

    assert interval_counter == 6
