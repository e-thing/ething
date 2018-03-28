
from .. import Action
from .. import InvalidRuleException


class DeviceRequest(Action):
	
	@staticmethod
	def validate (attributes, context):
		
		attributes.setdefault('device', None)
		attributes.setdefault('operation', None)
		attributes.setdefault('parameters', None)
		attributes.setdefault('output', None)
		
		dev = None
		
		for key in attributes:
			
			value = attributes[key]
			
			if key == 'device':
				
				if not isinstance(value, basestring):
					raise Exception("must be a device id.")
				
				dev = context['ething'].get(value)
				
				if not dev or not dev.isTypeof('Device'):
					raise Exception("the resource with id '%s' does not exist or is not a Device." % value)
				
				
			elif key == 'operation':
				
				if not( isinstance(value, basestring) and len(value)>0 ):
					raise Exception("must be a non empty string.")
			
			elif key == 'parameters':
				if not isinstance(value, dict) and value is not None:
					raise Exception("%s: invalid" % key)
			
			elif key == 'output':
				
				if not isinstance(value, dict) or 'type' not in value or not isinstance(value['type'], basestring) or 'name' not in value or not isinstance(value['name'], basestring):
					raise Exception("%s: invalid" % key)
				
				o = {
					'type': value['type'],
					'expireAfter': None,
					'name': value['name']
				}
				
				if value['type'] == 'File' or value['type'] == 'Table':
					
					if 'expireAfter' in value :
						if not isinstance(value['expireAfter'], int) or value['expireAfter']<0:
							raise Exception("%s: invalid" % key)
						o['expireAfter'] = value['expireAfter']
					
				else:
					raise Exception("output type can only File or Table.")
				
				attributes[key] = o
				
			else:
				raise Exception("%s: invalid" % key)
		
		if attributes['operation'] not in dev.interface.method_names:
			raise Exception("operation '%s' does not exist." % attributes['operation'])
		
		
		return True
	
	
	
	def call(self, signal):
		
		device = self.ething.get(self['device'])
		if not device:
			raise InvalidRuleException("The device %s does not exist any more" % str(device))
		
		kwargs = {}
		if self['parameters']:
			kwargs.update(self['parameters'])
		
		result = device.interface.call(self['operation'], **kwargs)
		
		output = self['output']
		if output:
			
			filename = output['name']
			
			if output['type'] == 'File':
				
				#does this file already exist !
				file = self.ething.findOne({
					'type' : 'File',
					'name' : filename,
					'createdBy' : device.id
				})
				
				if not file:
					# no, create it !
					opt = { 'name' : filename }
					if output['expireAfter'] is not None :
						opt['expireAfter'] = output['expireAfter']
					file = self.ething.create('File', opt, device)
				
				if file:
					file.write( str(result) )
				
			elif output['type'] == 'Table':
				
				#does this file already exist !
				table = self.ething.findOne({
					'type' : 'Table',
					'name' : filename,
					'createdBy' : device.id
				})
				
				if not table:
					# no, create it !
					opt = { 'name' : filename }
					if output['expireAfter'] is not None :
						opt['expireAfter'] = output['expireAfter']
					table = self.ething.create('Table', opt, device)
				
				if table:
					
					if isinstance(result, int) or isinstance(result, float) or isinstance(result, basestring) or isinstance(result, bool) or result is None:
						table.insert({
							'value': result
						})
					elif isinstance(result, dict):
						table.insert(result)
					else:
						raise Exception('unable to put the data in the output table')
			
		
	
	
	