
import json
import sys

def check_package( name ):
	
	res = True
	
	try:
		__import__(name, globals(), locals(), [], -1)
	except ImportError:
		res = False
		
	return res


package_list = [{
	'name': 'pyserial',
	'importName': 'serial'
},{
	'name': 'select',
	'importName': 'select'
}]
result = True

for package in package_list:
	
	res = check_package(package['importName'])
	if not res:
		result = False
		print 'module '+package['name']+' not found'
	
	
if result:
	sys.exit(0)
else:
	sys.exit(1)


