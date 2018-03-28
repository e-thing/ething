

"""
 @swagger-definition
 "MySensorsSerialGateway":{ 
   "type": "object",
   "description": "MySensorsSerialGateway Device resource representation",
	 "allOf": [
		{
		   "$ref":"#/definitions/MySensorsGateway"
		},
		{  
		   "type": "object",
		   "properties":{
			 "baudrate": {
				  "type":"number",
				  "description":"The baudrate (default to 115200)."
			   },
			 "port": {
				  "type":"string",
				  "description":"The serial port name."
			   }
		   }
		}
   ]
 }
"""


from MySensorsGateway import MySensorsGateway
from ething.base import attr, isString, isInteger, isEnum

@attr('baudrate', validator = isInteger() & isEnum([110,150,300,600,1200,2400,4800,9600,19200,38400,57600,115200]), default = 57600)
@attr('port', validator = isString())
class MySensorsSerialGateway(MySensorsGateway):
	pass





