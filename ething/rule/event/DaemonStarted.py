
from .. import Event

class DaemonStarted(Event):
	pass


if __name__ == '__main__':
	
	print DaemonStarted.emit()