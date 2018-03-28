"""
 @author Adrien Mezerette <a.mezerette@gmail.com>
 @version 0.1.0
 @package ething
"""

from webserver.WebServer import WebServer
import pymongo
from DbFs import DbFs
from ResourceQueryParser import ResourceQueryParser
from Config import Config
from SignalManager import SignalManager
from SocketManager import SocketManager
from TaskManager import TaskManager
from Scheduler import Scheduler
from Mail import Mail
from rpc import RPC
from version import __version__
import rule
import logging
import sys
import os
import datetime
import re

from meta import get_resource_class

from File import File
from Table import Table
from App import App

from rflink import RFLink
from mysensors import MySensors
from mqtt import MQTT
from yeelight import Yeelight
from mihome import Mihome
from zigate import Zigate
from device.Http import Http
from device.RTSP import RTSP
from device.SSH import SSH




class Core(object):
	
	__instance = None
	
	@staticmethod
	def getInstance():
		return Core.__instance
	
	
	
	def __init__(self, config = None):
		self.running = False
		
		self.config = Config(self, config)
		
		self._init_logger()
		self._init_database()
		self._init_rpc()
		
		Core.__instance = self
		
	
	def _init_logger(self):
		self.log = logging.getLogger('ething')
		self.log.setLevel(getattr(logging, self.config['log']['level'].upper(), logging.INFO))
	
	
	def _init_webserver(self):
		if self.config['webserver']['enabled']:
			self.webserver = WebServer(self)
			self.webserver.start()
	
	def _init_database(self):
		
		try :
			server = 'mongodb://' + self.config['db']['host'] + ':' + str(self.config['db']['port'])
			mongoClient = pymongo.MongoClient(server, username=self.config['db']['user'], password=self.config['db']['password'], connect = False)
			self.db = mongoClient[self.config['db']['database']]
			if self.db is None:
				raise Exception('unable to connect to the database')
			
		except:
			raise Exception('unable to connect to the database [%s]' % sys.exc_info()[1])
		
		self.fs = DbFs(self.db)
		
		self.resourceQueryParser = ResourceQueryParser()
	
	
	def _init_rpc(self):
		self.rpc = RPC(self)
	
	
	def stop(self):
		self.log.info("stopping ...")
		self.running = False
	
	@property
	def version(self):
		return __version__
	
	def destroy(self):
		
		self.log.info("cleaning for exit")
		
		self.running = False
		
		if hasattr(self, "webserver"):
			try:
				self.webserver.stop()
			except Exception as e:
				self.log.exception("error while shutting down webserver")
		
		if hasattr(self, "rflink"):
			try:
				self.rflink.stop_all_controllers()
			except Exception as e:
				self.log.exception("error while shutting down rflink")
		
		if hasattr(self, "mysensors"):
			try:
				self.mysensors.stop_all_controllers()
			except Exception as e:
				self.log.exception("error while shutting down mysensors")
		
		if hasattr(self, "mqtt"):
			try:
				self.mqtt.stop_all_controllers()
			except Exception as e:
				self.log.exception("error while shutting down mqtt")
		
		if hasattr(self, "yeelight"):
			try:
				self.yeelight.stop_all_controllers()
			except Exception as e:
				self.log.exception("error while shutting down yeelight")
		
		if hasattr(self, "mihome"):
			try:
				self.mihome.stop_controller()
			except Exception as e:
				self.log.exception("error while shutting down mihome")
		
		if hasattr(self, "taskManager"):
			try:
				self.taskManager.terminate()
			except Exception as e:
				self.log.exception("error while shutting down taskManager")
		
		if hasattr(self, "rpc_server"):
			try:
				self.rpc_server.stop()
			except Exception as e:
				self.log.exception("error while shutting down rpc")
		
	
	
	def restart(self):
		self.destroy()
		chdir(owd)
		
		os.execl(sys.executable, sys.executable, *sys.argv)
		sys.exit(0)
	
	def start(self):
		
		self.log.info("Starting ething %s" % self.version)
		self.log.info("Using home directory: %s" % os.getcwd())
		
		self._init_webserver()
		
		self.scheduler = Scheduler(self)
		self.taskManager = TaskManager(self)
		self.signalManager = SignalManager(self)
		self.socketManager = SocketManager(self)
		self.ruleManager = rule.Manager(self)
		self.mail = Mail(self)
		
		self.rpc.register('stop', self.stop)
		self.rpc.register('version', self.version)
		
		def _notify(*args, **kwargs):
			self.taskManager.run(self.mail.send, args=args, kwargs=kwargs, name = 'mail')
		
		self.rpc.register('notify', _notify)
		
		# rpc
		self.rpc_server = self.rpc.start_server(self.socketManager)
		
		# load the controllers
		self.rflink = RFLink(self)
		self.mysensors = MySensors(self)
		self.mqtt = MQTT(self)
		self.yeelight = Yeelight(self)
		self.mihome = Mihome(self)
		self.zigate = Zigate(self)
		
		self.scheduler.at(self._tick, '*', '*') # every minute
		
		self.scheduler.at(self._ping, '*', '*') # every minute
		
		self.signalManager.addDispatcher( lambda signal: self.rpc.publish('signal', signal) )
		
		self.running = True
		
	
	def loop(self, timeout = 1):
		self.socketManager.loop(timeout)
		self.scheduler.update()
		self.taskManager.loop()
	
	def loop_forever(self):
		while self.running:
			self.loop(1)
			
	
	def _tick(self):
		"""
		dispatch the tick event
		"""
		self.log.debug("tick...")
		self.dispatchSignal(rule.event.Timer.emit())
	
	
	def _ping(self):
		"""
		ping all devices to see if there are still connected !
		"""
		
		self.log.debug("ping...")
		
		for task in self.taskManager.tasks:
			if task.name == 'ping':
				if (not task.is_started) or task.is_running:
					self.log.warning("ping task stil running")
					return # this task is still running
		
		
		def ping():
			devices = self.find({
				'extends': 'Device'
			})
			
			for device in devices:
				if hasattr(device, 'ping'):
					if (device.lastSeenDate is None) or (device.lastSeenDate < datetime.datetime.utcnow()-datetime.timedelta(seconds=45)):
						device.ping()
				
		
		
		self.taskManager.run(ping, name = 'ping')
		
	
	
	
	
	#
	# Resources
	#
	
	
	def find (self, query = None, limit = None, skip = None, sort = None):
		
		if query is None:
			query = {}
		
		if isinstance(query, basestring):
			# parse the query string
			query = self.resourceQueryParser.parse(query)
		
		
		c = self.db["resources"]
		
		resources = []
		
		opt = {}
		
		if limit is None:
			limit = 0
		if skip is None:
			skip = 0
		
		if isinstance(sort, basestring):
			m = re.search('^([+-]?)(.+)$', sort)
			if m is not None:
				sort = [(m.group(2), pymongo.ASCENDING if m.group(1)!='-' else pymongo.DESCENDING)]
			else:
				sort = None
		
		if sort is None:
			sort = [('modifiedDate', pymongo.DESCENDING)]
		
		
		cursor = c.find(query, skip=skip, limit=limit, sort=sort)
		
		for doc in cursor:
			cl = get_resource_class(doc['type'])
			if cl is not None:
				resources.append(cl(self, doc))
		
		return resources
	
	
	def findOne (self, query = None):
		r = self.find(query,1)
		return r[0] if len(r)>0 else None
	
	
	def get (self, id):
		return self.findOne({'_id' : id})
	
	
	def create (self, type, attributes):
		cl = get_resource_class(type)
		if cl is not None:
			return cl.create(self, attributes)
		else:
			raise Exception('the type "%s" is unknown' % type)
	
	
	def usage(self):
		
		# table
		tbinfo = {
			'count' : 0,
			'size' : 0
		}
		
		for name in self.db.collection_names(include_system_collections=False):
			if re.match('tb\.', name):
				try:
					i = self.db.command('collstats',name)
					tbinfo['count'] += i['count']
					tbinfo['size'] += i['size']
				except:
					pass
		
		# other
		resource_size = 0
		c = self.db["resources"]
		res = c.aggregate([{
			'$match' : {
				"size" : {'$exists' : True}
			}
		},{
			'$group' : {
				"_id" : None,
				"size" : {'$sum' : 'size'}
			}
		}])
		
		try:
			result = res.next()
			resource_size = result["size"]
		except:
			pass
		
		res.close()
		
		return {
			'used' : (resource_size + tbinfo['size'])
		}
	
	
	#
	# Rules
	#
	
	def findRules (self, query = {}):
		rules = []
		c = self.db["rules"]
		cursor = c.find(query, sort=[('priority', pymongo.DESCENDING)])
		for doc in cursor:
			rules.append(rule.Rule(self, doc))
		
		return rules
	
	
	def getRule (self, id):
		r = self.findRules({
			'_id' : id
		})
		return r[0] if len(r) else None
	
	
	def createRule (self, attr):
		return rule.Rule.create(self,attr)
	
	
	@staticmethod
	def r_encode (data, showPrivateField = True):
		o={}
		for k in data:
			
			v = data[k]
			
			if k == '_id':
				k = 'id'
			
			if k[0] != '_':
				if k[0] == '#': # show the hidden field (apikey ...)
					if not showPrivateField:
						continue
					k = k[1:]
				
				if isinstance(v, datetime.datetime):
					o[k] = v.isoformat()
				elif isinstance(v, dict):
					o[k] = Core.r_encode(v)
				else:
					o[k] = v
		
		return o
	
	def dispatchSignal (self, signal, *args, **kwargs):
		try:
			if isinstance(signal, basestring):
				cls = get_event_class(signal)
				if not cls:
					return
				signal = cls.emit(*args, **kwargs)
			
			#self.log.debug('dispatchSignal %s' % signal)
			self.rpc.send('signal', signal)
			
		except:
			pass
		
		# if hasattr(self, "signalManager"):
		# 	self.signalManager.dispatch(signal)
	
	def notify (self, *args, **kwargs):
		
		self.rpc.send('notify', *args, **kwargs)
		
		# if hasattr(self, "signalManager"):
		# 	self.signalManager.dispatch(signal)
	
	def reset(self):
		"""
		clear all the database !
		"""
		db_name = self.db.name
		db_client = self.db.client
		db_client.drop_database(db_name)
		self.db = db_client[db_name]
		
		
	

		
def test_db():
	
	core = Core({
		'db':{
			'database': 'test'
		},
		'log':{
			'level': 'debug'
		}
	})
	
	print core.find()
	print core.usage()
	


if __name__ == "__main__":
	test_db()
