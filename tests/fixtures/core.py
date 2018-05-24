# coding: utf-8
import pytest
from ething.core import Core
import os
import tempfile


@pytest.fixture
def core():
    core = Core({
        'db': {
            'database': 'test_unit'
        },
        'log': {
            'level': 'debug'
        },
        'debug': True,
        'webserver': {
            'enabled': False,
            'port': 8001
        },
        'rpc': {
            'address': os.path.join(tempfile.gettempdir(), './ething_socket_test')
        }
    })

    core.reset()

    return core


from ething.SignalManager import SignalManager
from ething.SocketManager import SocketManager
from ething.TaskManager import TaskManager
from ething.Scheduler import Scheduler
from ething.Mail import Mail


@pytest.fixture
def core_extended(core):
    core.scheduler = Scheduler(core)
    core.taskManager = TaskManager(core)
    core.signalManager = SignalManager(core)
    core.socketManager = SocketManager(core)
    core.mail = Mail(core)

    return core
