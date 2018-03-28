
from .RuleItem import RuleItem
from . import InvalidRuleException
from ething.meta import MetaAction

class Action(RuleItem):
	
	__metaclass__ = MetaAction
	
	def execute(self, signal):
		if self.valid:
			
			# reset error
			self.error = False
			
			try:
				self.call(signal)
			
			except InvalidRuleException as e:
				# this exception is fired when this action is no more valid.
				self.valid = False
				self.error = e
				self.ething.log.exception("Fatal error in action %s" % self)
			
			except Exception as e:
				self.error = e
				self.ething.log.exception("Error in action %s" % self)
	
	
	def call(self, signal):
		raise NotImplementedError()

 