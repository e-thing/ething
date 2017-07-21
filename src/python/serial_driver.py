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

serialToStdoutBuf = "";
stdinToSerialBuf = "";

inputs = [sys.stdin];
outputs = [];

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
	
	print >>sys.stderr, '\nwaiting for the next event %d %d' % (len(inputs), len(outputs))
	
	readable, writable, exceptional = select.select(inputs, outputs, inputs, 10.)
	
	
	# Handle inputs
	for s in readable:
		
		if s is sys.stdin:
			
			data = sys.stdin.read(1024)
			
			print >>sys.stderr, 'stdin incoming data %d bytes (%s)' %(len(data), data)
			
			if data:
				print >>sys.stderr, 'received "%s"' % (data)
				stdinToSerialBuf += data
				outputs.append(ser.fileno())
			else:
				print >>sys.stderr, 'empty'
		else:
			
			print >>sys.stderr, 'serial incoming data'
			
			ser_av = ser.inWaiting()
			if ser_av:
				print >>sys.stderr, 'received %d bytes' % (ser_av)
				serialToStdoutBuf += ser.read(ser_av)
				outputs.append(sys.stdout)
			else:
				print >>sys.stderr, 'empty'
	
	# Handle outputs
	for s in writable:
		
		if s is sys.stdout:
			
			print >>sys.stderr, 'write to stdout'
			
			sys.stdout.write(serialToStdoutBuf);
			sys.stdout.flush()
			serialToStdoutBuf = '';
			outputs.remove(s)
			
		else:
			
			print >>sys.stderr, 'write to serial'
			
			ser.write(stdinToSerialBuf[:SERIAL_CHUNK_SIZE]);
			stdinToSerialBuf = stdinToSerialBuf[SERIAL_CHUNK_SIZE:];
				
			if len(stdinToSerialBuf)==0:
				outputs.remove(s)
		
	
	# Handle "exceptional conditions"
	for s in exceptional:
		print >>sys.stderr, 'handling exceptional'
		ser.close();
		exit(3);
	
	##time.sleep(0.1)
	
	
	# heartbeat
	f = open("/var/log/heartbeat.txt","w")
	f.write(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
	f.close()
 
 


