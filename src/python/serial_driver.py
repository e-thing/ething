# works with Python 2.7.9

import serial
import time
import sys
import select


# Add O_NONBLOCK to the stdin descriptor flags 
import fcntl, os
flags = fcntl.fcntl(0, fcntl.F_GETFL)
fcntl.fcntl(0, fcntl.F_SETFL, flags | os.O_NONBLOCK)


SERIAL_CHUNK_SIZE = 256

serialToStdoutBuf = ""
stdinToSerialBuf = ""

inputs = [sys.stdin]
outputs = []





if len(sys.argv) != 3:
	print >>sys.stderr, "invalid arguments, usage: <port> <baudrate>"
	exit(1)



# open serial port
try:
	ser = serial.Serial(sys.argv[1], int(sys.argv[2]), timeout=0)
	inputs.append(ser.fileno())
except:
	print >>sys.stderr, "unable to open the serial port"
	exit(2)




	
while inputs:
	
	readable, writable, exceptional = select.select(inputs, outputs, inputs, 10.)
	
	
	# Handle inputs
	for s in readable:
		
		if s is sys.stdin:
			
			data = sys.stdin.read(1024)
			
			if data:
				stdinToSerialBuf += data
				outputs.append(ser.fileno())
			
		else:
			
			ser_av = ser.inWaiting()
			if ser_av:
				serialToStdoutBuf += ser.read(ser_av)
				outputs.append(sys.stdout)
	
	# Handle outputs
	for s in writable:
		
		if s is sys.stdout:
			
			sys.stdout.write(serialToStdoutBuf)
			sys.stdout.flush()
			serialToStdoutBuf = ''
			outputs.remove(s)
			
		else:
			
			ser.write(stdinToSerialBuf[:SERIAL_CHUNK_SIZE])
			stdinToSerialBuf = stdinToSerialBuf[SERIAL_CHUNK_SIZE:]
				
			if len(stdinToSerialBuf)==0:
				outputs.remove(s)
		
	
	# Handle "exceptional conditions"
	for s in exceptional:
		ser.close()
		exit(3)
	
	##time.sleep(0.1)
	
	
 
 


