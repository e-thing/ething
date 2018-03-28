
from Controller import Controller
from YeelightDevice import YeelightDevice, Device
from YeelightBulbRGBW import YeelightBulbRGBW



class Yeelight(object):
	
	
	def __init__(self, core):
		self.core = core
		self.log = core.log
		self.rpc = core.rpc
		
		self.controllers = {}
		
		self.rpc.register('device.yeelight.send', self.controller_send, callback_name = 'callback')
		self.rpc.register('device.yeelight.sendWaitResponse', self.controller_send_wait_response, callback_name = 'callback')
		
		self.core.signalManager.bind('ResourceCreated', self.on_resource_created)
		self.core.signalManager.bind('ResourceDeleted', self.on_resource_deleted)
		
		devices = self.core.find({
			'type' : { '$regex': '^Yeelight.*$' }
		})
		
		for device in devices:
			try:
				self.start_controller(device)
			except Exception as e:
				self.log.error(e)
	
	
	
	def on_resource_created(self, signal):
		device = self.core.get(signal['resource'])
		if isinstance(device, YeelightDevice):
			self.start_controller(device)
		
	
	def on_resource_deleted(self, signal):
		device = self.core.get(signal['resource'])
		if isinstance(device, YeelightDevice):
			self.stop_controller(device)
		
	def start_controller (self, device):
		
		if isinstance(device, basestring):
			device = self.core.get(device)
		
		if not device or not isinstance(device, YeelightDevice):
			raise Exception("the device %s does not exist or has the wrong type" % str(device))
		
		# remove any previous stream from this device
		self.stop_controller(device)
		
		self.log.info("starting Yeelight controller '%s' id=%s type=%s" % (device.name, device.id, device.type))
		
		controller = Controller(device)
		
		self.controllers[device.id] = controller
		
		return controller
	
	
	def stop_controller (self, device):
		
		if isinstance(device, Device):
			device = device.id
		
		if device in self.controllers:
			controller = self.controllers[device]
			self.log.info("stopping Yeelight controller '%s' id=%s type=%s" % (controller.device.name, controller.device.id, controller.device.type))
			controller.destroy()
			del self.controllers[device]
	
	
	def stop_all_controllers(self):
		for id in self.controllers.keys():
			self.stop_controller(id)
		self.controllers = {}
	
	def controller_send(self, device_id, message, callback):
		
		if device_id in self.controllers:
			
			controller = self.controllers[device_id]
			
			controller.send(message, callback = callback)
			
		else:
			raise Exception("unknown Yeelight instance for device id %s" % device_id)
	
	
	def controller_send_wait_response(self, device_id, message, callback):
		
		if device_id in self.controllers:
			
			controller = self.controllers[device_id]
			
			controller.send(message, callback = callback, waitResponse = True)
			
		else:
			raise Exception("unknown Yeelight instance for device id %s" % device_id)
		
	
	
