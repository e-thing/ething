

import serial.tools.list_ports
import json


ports = list(serial.tools.list_ports.comports())

info = [];

for port in ports:
	info.append({
		'device': port.device,
		'name': port.name,
		'description': port.description,
		'hwid': port.hwid,
		'vid': port.vid,
		'pid': port.pid,
		'serial_number': port.serial_number,
		'location': port.location,
		'manufacturer': port.manufacturer,
		'product': port.product,
		'interface': port.interface
	})


print json.dumps(info, indent=4)

