

"""
 @swagger-definition
 "Device\\ZigateSerialGateway":{ 
   "type": "object",
   "description": "ZigateSerialGateway Device resource representation",
	 "allOf": [
		{
		   "$ref":"#/definitions/Device\\ZigateGateway"
		},
		{  
		   "type": "object",
		   "properties":{
			 "port": {
				  "type":"string",
				  "description":"The serial port name."
			   }
		   }
		}
   ]
 }
"""
	 
from ZigateGateway import ZigateGateway, attr, isString


@attr('port', validator = isString())
class ZigateSerialGateway (ZigateGateway):
	pass
	
	




