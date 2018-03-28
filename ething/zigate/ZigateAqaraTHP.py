

"""
 @swagger-definition
 "Device\\ZigateAqaraTHP":{ 
   "type": "object",
   "description": "Mihome temperatire/humidity/pressure Sensor Device class.",
	 "allOf": [
		{
		   "$ref":"#/definitions/ZigateDevice"
		},
		{  
		   "type": "object",
		   "properties":{}
		}
   ]
 }
"""



from ZigateDevice import ZigateDevice
import Zigate


@Zigate.model('lumi.weather', 'thermometer himidity pressure sensor')
class ZigateAqaraTHP(ZigateDevice):
	
	def onMessage (self, message):
		pass # todo
		
		
	





 