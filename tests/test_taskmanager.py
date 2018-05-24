# coding: utf-8
import pytest
from ething.TaskManager import TaskManager
import time


def test_taskmanager(core):

    manager = TaskManager(core, max_running_tasks=2)

    def sleep(sec):
        time.sleep(sec)

    for i in range(0, 4):
        manager.run(sleep, args=(i+1, ), name=('task %d' % i))

    manager.loop()

    assert len(manager.running_tasks) == 2  # task 1 & 2

    time.sleep(1.2)

    assert len(manager.running_tasks) == 1  # task 2

    manager.loop()

    assert len(manager.running_tasks) == 2  # task 2 & 3

    time.sleep(1)

    manager.loop()

    time.sleep(4.1)

    manager.loop()

    assert len(manager.running_tasks) == 0
