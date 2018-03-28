

import yeelight as Yeelight
import socket
import time
import json
import random


class Controller (object):
	
	AUTOCONNECT_PERIOD = 60; # seconds	
	RESPONSE_TIMEOUT = 10; # seconds	
	CONNECT_TIMEOUT = 2; # seconds	
	
	reset_attr = ['host']
	
	
	
	def __init__ (self, device):
		
		self._device = device
		self._ething = device.ething
		self._isOpened = False
		
		self._log = device.ething.log
		
		self._sock = None
		
		self._lastState = False
		self._lastAutoconnectLoop = 0
		self._preventFailConnectLog = 0
		self._lastActivity = 0
		
		self._buffer = ""
		
		# response management
		self._responseListeners = []
		
		# refresh the gateway each time the gateway properties changes
		self.ething.signalManager.bind('ResourceMetaUpdated', self.onResourceMetaUpdated)
		
		self.ething.scheduler.tick(self.update)
	
	
	@property
	def device (self):
		return self._device
	
	@property
	def log (self):
		return self._log
	
	@property
	def ething (self):
		return self._ething
	
	@property
	def isOpened (self):
		return self._sock is not None
	
	@property
	def socket (self):
		return self._sock
	
	def onResourceMetaUpdated(self, signal):
		if signal['resource'] == self.device.id and signal['rModifiedDate'] > self.device.modifiedDate :
			self.device.refresh()
			
			for attr in signal['attributes']:
				if attr in Controller.reset_attr:
					self.restart()
					break
	
	def destroy(self):
		self.close()
		self.ething.signalManager.unbind('ResourceMetaUpdated', self.onResourceMetaUpdated);
	
	
	def open (self):
		self._lastAutoconnectLoop = time.time()
		
		if self.isOpened:
			return True
		
		host = self.device.host
		
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.settimeout(Controller.CONNECT_TIMEOUT)
		
		try:
			self._sock.connect((host, Yeelight.PORT))
		except socket.error as e:
			raise Exception("Yeelight: unable to connect to the device %s : %s" % (host,str(e)))
		
		self._sock.setblocking(0)
		
		self.ething.socketManager.registerReadSocket(self._sock, self.onDataAvailable)
		
		self._lastActivity = time.time()
		self._buffer = ''
		
		self.log.info("Yeelight: connected to %s" % host)
		
		self.device.setConnectState(True)
		
		return True
	
	def readline(self):
		p = self._buffer.find("\n")
		if p>=0 :
			line = self._buffer[0:p]
			self._buffer = self._buffer[p+1:]
			return line.rstrip()
		
		return None
	
	def onDataAvailable (self):
		
		
		chunk = self._sock.recv(1024)
		if not chunk:
			# connection broken
			self.close()
			return
		
		self._buffer += chunk
		
		self._lastActivity = time.time()
		
		
		while True:
			line = self.readline()
			if line is not None:
				
				self.log.debug("Yeelight: message received = %s" % line)
				
				try:
					
					# must be json
					message = json.loads(line)
					
					self.processMessage(message)
					
				except Exception as e:
					# skip the line
					self.log.exception("Yeelight: unable to handle the message %s" % (line))
					continue
			else:
				break
	
	
	
	
	
	
	def close (self):
		if self.isOpened:
			self.ething.socketManager.unregisterReadSocket(self._sock)
			self._sock.close()
			self._sock = None
			
			self.device.setConnectState(False)
			
			for responseListener in self._responseListeners:
				responseListener['callback']('disconnected', None);
			self._responseListeners = []
			
			self.log.info("Yeelight: closed")
			
	
	
	"""
	exemple of messages : (https://www.yeelight.com/download/Yeelight_Inter-Operation_Spec.pdf)
		// response to the query {"id":1,"method":"get_prop","params":["power", "not_exist", "bright"]}
		{"id":1, "result":["off","","100"]}
		// notifications
		{"method":"props","params":{"power":"on"}}
		{"method":"props","params":{"power":"off"}}
		
	"""
	def processMessage (self, message):
		
		with self._device as device:
			
			device.setConnectState(True)
			
			if "id" in message:
				
				responseId = int(message["id"])
				responseResult = message["result"] if "result" in message else []
				
				i = 0
				while i < len(self._responseListeners):
					responseListener = self._responseListeners[i]
					
					if responseListener['id'] == responseId:
						
						# remove this item
						self._responseListeners.pop(i)
						i -= 1
						
						if callable(responseListener['callback']):
							responseListener['callback'](False, responseResult)
						
						break
					
					i += 1
				
			elif ("method" in message) and ("params" in message):
				# notification
				
				method = message["method"]
				params = message["params"]
				
				if method == "props":
					if params:
						device.storeData(params)
					
				else:
					raise Exception('unknown method %s' % str(method))
				
				
			else:
				raise Exception('unable to parse the message')
		
	
	
	
	# Retrieve and return the properties of the device.
	def refresh (self):
		
		device = self._device
		
		requestedProperties = [
            "power", "bright", "ct", "rgb", "hue", "sat",
            "color_mode", "flowing", "delayoff", "flow_params",
            "music_on", "name"
        ]
		
		def cb(error, messageSent, response):
			
			if not error and isinstance(response, list) and len(response) == len(requestedProperties):
				
				# some formatting
				for i in range(0, len(response)):
					if response[i].decode('utf8').isnumeric():
						response[i] = int(response[i])
				
				params = dict(zip(requestedProperties, response))
				
				device.storeData(params)
		
		
		self.send({
			"method" : "get_prop",
			"params" : requestedProperties
		}, cb, True)
		
	
	
	
	def update (self):
		
		# do some stuff regularly
		now = time.time()
		
		# check for a deconnection
		if not self.isOpened and self.isOpened != self._lastState:
			self.log.info("Yeelight: disconnected")
		self._lastState = self.isOpened
		
		# autoconnect
		if not self.isOpened and (now - self._lastAutoconnectLoop) > Controller.AUTOCONNECT_PERIOD:
			try:
				self._lastAutoconnectLoop = now
				self.open()
				self._preventFailConnectLog = 0
			except Exception as e:
				
				if self._preventFailConnectLog % 20 == 0:
					self.log.warn("Yeelight: unable to connect : %s" % e.message)
				self._preventFailConnectLog += 1
		
		# check for timeout !
		i = 0
		while i < len(self._responseListeners):
			responseListener = self._responseListeners[i]
			
			if now - responseListener['ts'] > Controller.RESPONSE_TIMEOUT:
				
				# remove this item
				self._responseListeners.pop(i)
				i -= 1
				
				responseListener['callback']('response timeout', None)
			
			i += 1
		
	
	
	
	"""
	 $message message to send
	 $callback (optional) function($error, $messageSent, $messageReceived = null)
	 $waitResponse (optional) true|false wait for a response or not
	"""
	def send (self, message, callback = None, waitResponse = None):
		
		if self.isOpened:
			
			message['id'] = random.randint(1,9999)
			
			self.log.debug("Yeelight: message send %s" % str(message))
			
			self._lastActivity = time.time()
			
			wb = self._sock.send(json.dumps(message)+"\r\n")
			
			if waitResponse:
				# wait for a response
				
				def cb(error, messageReceived):
					if callable(callback):
						callback(error, message, messageReceived)
				
				self._responseListeners.append({
					'callback' : cb,
					'ts' : time.time(),
					'messageSent' : message,
					'id' : message['id']
				})
				
			else:
				if callable(callback):
					callback(False, message, None)
			
			return wb
		
		else:
			
			if callable(callback):
				callback('not connected', message, None)
			
			return 0
	
	



