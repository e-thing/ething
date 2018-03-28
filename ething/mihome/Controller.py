


from Mihome import *
import socket
import time
import json


class Controller(object):
	
	AUTOCONNECT_PERIOD = 60 # seconds
	RESPONSE_TIMEOUT = 10
	ACTIVITY_TIMEOUT = 3600 # 1 hour
	
	
	def __init__ (self, ething):
				
		self._ething = ething
		
		self._log = ething.log
		
		self._lastState = False
		self._lastAutoconnectLoop = 0
		self._preventFailConnectLog = 0
		
		# response management
		self._responseListeners = []
		
		# activity management
		self._activities = {}
		
		self._socketManager = self.ething.socketManager
		
		self._sock = None
		
		self.ething.scheduler.tick(self.update)
	
	@property
	def ething (self):
		return self._ething
	
	@property
	def log (self):
		return self._log
	
	@property
	def isOpened (self):
		return self._sock is not None
	
	def restart(self):
		if self.isOpened:
			self.close()
			self.open()
	
	def destroy(self):
		self.close()
	
	
	def open (self):
		
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			
			sock.bind(("0.0.0.0", MULTICAST_PORT))
			
			mreq = struct.pack("=4sl", socket.inet_aton(MULTICAST_ADDRESS), socket.INADDR_ANY)
			sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
			sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCKET_BUFSIZE)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allow multiple processes to bind to the same address
			sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq) # join multicast group and bind to port
			sock.setblocking(0)
			
			self._sock = sock
			
			self._socketManager.registerReadSocket(self._sock, self.process)
			
			self.log.info("[Mihome]: connection opened, host: %s , port: %d" % (str(MULTICAST_ADDRESS), MULTICAST_PORT))
		except Exception as e:
			self.log.exception("[Mihome] open error")
			self._sock = None
			return False
		
		self._lastAutoconnectLoop = 0
		return True
	
	
	def close (self):
		
		if self._sock:
			self._socketManager.unregisterReadSocket(self._sock)
			self._sock.close()
			self._sock = None
		
		for responseListener in self._responseListeners:
			responseListener['callback']('disconnected', None);
		self._responseListeners = []
		
		self.log.info("Mihome: closed")
		
		return True
	
	
	
	
	
	lastActivity = 0
	
	buffer = ""
	
	
	
	
	
	
	@staticmethod
	def extract (arr, keys):
		ret = {}
		for k in keys:
			ret[k] = arr.get(k)
		return ret
	
	
	def process (self):
		
		data, addr = self._sock.recvfrom(SOCKET_BUFSIZE)
		
		if not data:
			# receiving data failed : remote side rejected one of our packets
			# due to the nature of UDP, there's no way to tell which one exactly
			# peer is not filled either
			self.log.error("Mihome: receive error")
			self.close()
			return
		
		
		self.log.debug("Mihome: receive data from %s : %s" % (str(addr), data))
		
		response = json.loads(data.decode("utf-8"))
		response_data = json.loads(response.get('data', '{}'))
		
		if isinstance(response, dict):
			
			sid = response.get('sid')
			cmd = response.get('cmd')
			
			self._activities[sid] = time.time()
				
			if cmd == 'heartbeat'or cmd == 'report' or cmd == 'read_ack':
				
				"""
				 {"cmd":"report","model":"gateway","sid":"34ce00fb61a9","short_id":0,"data":"{\"rgb\":0,\"illumination\":503}"}
				 {"cmd":"report","model":"weather.v1","sid":"158d0001a4b64a","short_id":22319,"data":"{\"temperature\":\"1983\"}"}
				 {"cmd":"report","model":"weather.v1","sid":"158d0001a4b64a","short_id":22319,"data":"{\"humidity\":\"3914\"}"}
				 {"cmd":"heartbeat","model":"gateway","sid":"34ce00fb61a9","short_id":"0","token":"JxtPXoxj2FmBrTqA","data":"{\"ip\":\"192.168.1.8\"}"}
				 {"cmd":"heartbeat","model":"sensor_magnet.aq2","sid":"158d0001d84e77","short_id":10731,"data":"{\"voltage\":2965,\"status\":\"close\"}"}
				"""
				
				if response.get('model') == 'gateway':
					# concerning a gateway
					
					gatewayDevice = self.ething.findOne({
						'type' : 'MihomeGateway',
						'sid' : sid
					})
					
					if not gatewayDevice:
						ip = response_data.get('ip')
						
						if ip:
							gatewayDevice = self.ething.create('MihomeGateway', {
								'name' : 'gateway',
								'sid' : sid,
								'ip': ip
							})
							if not gatewayDevice:
								self.log.error("Mihome: unable to create the gateway sid:%s" % sid)
						
					
					
					if gatewayDevice:
						with gatewayDevice:
							gatewayDevice.setConnectState(True)
							gatewayDevice.processData(response)
					
					
					
				else:
					# concerning a device
					
					device = self.ething.findOne({
						'extends' : 'MihomeDevice',
						'sid' : sid
					})
					
					if not device:
						
						model = response.get('model')
						
						if model == 'sensor_ht' or model == 'weather.v1':
							device = self.ething.create('MihomeSensorHT', {
								'name' : 'thermometer',
								'sid': sid
							})
						
						
						
						if not device:
							self.log.error("Mihome: unable to create the device model: %s , sid:%s" % (model, sid))
						
						
					
					
					if device:
						with device:
							device.setConnectState(True)
							device.processData(response)
					
			elif cmd == 'write_ack':
				pass
			else:
				self.log.warn("Mihome: received unk command %s" % cmd)
				
			
			
			if cmd in ['read_ack', 'write_ack', 'get_id_list_ack']:
				
				# response ?
				
				i=0
				while i < len(self._responseListeners):
					responseListener = self._responseListeners[i]
					
					if responseListener['sid'] == sid and responseListener['ack'] == cmd:
						
						# remove this item
						self._responseListeners.pop(i)
						i-=1
						
						if callable(responseListener['callback']):
							responseListener['callback'](False, responseListener['command'], response)
					
					i+=1
				
				
			
			
		

	
	
	
	
	def sendData (self, gateway, command, callback = None):
		if command.get('cmd') == 'write' and isinstance(command.get('data'), dict):
			command['data']['key'] = gateway.getGatewayKey()
		
		return self.sendCommand(command, callback, gateway.ip)
	
	
	def sendCommand (self, command, callback = None, addr = MULTICAST_ADDRESS):
		commandStr = json.dumps(command).encode("utf-8")
		
		if self.isOpened:
			
			self.log.debug("Mihome: send data to %s : %s" % (addr, commandStr))
			
			try:
				self._sock.sendto(commandStr, (addr, MULTICAST_PORT))
			except:
				if callable(callback):
					callback('send error', command, None)
			else:
				if callable(callback):
					cmd = command.get('cmd')
					sid = command.get('sid')
					
					self._responseListeners.append({
						'callback' : callback,
						'ts' : time.time(),
						'sid' : sid,
						'ack' : cmd + '_ack',
						'command' : command
					})
				
			
		else:
			if callable(callback):
				callback('not connected', command, None)
			
		
	
	def update (self):
		# do some stuff regularly
		now = time.time()
		
		# check for a deconnection
		if not self.isOpened and self.isOpened != self._lastState:
			self.log.info("Mihome: disconnected")
		self._lastState = self.isOpened
		
		# autoconnect
		if not self.isOpened and (now - self._lastAutoconnectLoop) > Controller.AUTOCONNECT_PERIOD:
			try:
				self._lastAutoconnectLoop = now
				self.open()
				self._preventFailConnectLog = 0
			except Exception as e:
				
				if self._preventFailConnectLog % 20 == 0:
					self.log.warn("Mihome: unable to connect : %s" % e.message)
				self._preventFailConnectLog += 1
		
		# check for timeout !
		i = 0
		while i < len(self._responseListeners):
			responseListener = self._responseListeners[i]
			
			if now - responseListener['ts'] > Controller.RESPONSE_TIMEOUT:
				
				# remove this item
				self._responseListeners.pop(i)
				i -= 1
				
				responseListener['callback']('response timeout', responseListener['command'], None)
			
			i += 1
		
		# _activities check
		for sid, lastActivity in self._activities.iteritems():
			if now - lastActivity > Controller.ACTIVITY_TIMEOUT :
				
				# remove this item
				del self._activities[sid]
				
				device = self.ething.findOne({
					'sid' : sid
				})
				
				if device:
					device.setConnectState(False)
				
				
	


