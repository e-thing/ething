# coding: utf-8
import pytest
from ething.Scheduler import Scheduler
import time


interval_counter = 0

def test_taskmanager(core):
    global interval_counter

    interval_counter = 0

    scheduler = Scheduler(core)

    def increase():
        global interval_counter
        interval_counter = interval_counter + 1

    scheduler.setInterval(0.5, increase)

    tf = time.time() + 3.2
    while time.time() < tf:
        scheduler.update()
        time.sleep(0.2)

    assert interval_counter == 6
