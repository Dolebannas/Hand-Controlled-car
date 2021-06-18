import socket
import time
import board
from adafruit_motorkit import MotorKit
from multiprocessing import Process,Pipe


def control(child_conn):
	# Define motorkit object to read from I2C
	kit = MotorKit(i2c=board.I2C())
	
	# Initialize UDP connection with recieving socket
	UDP_IP 	= "192.168.1.114"
	UDP_PORT = 5005	
	
	sock = socket.socket(socket.AF_INET, # Internet
	                     socket.SOCK_DGRAM) # UDP
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((UDP_IP, UDP_PORT))
	counter = 0
	try: 
		while True:
			data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
			# print("received message: %s" % data)
			message = (data.decode("utf-8")).split('_') #convert byte to an array of the two pieces of information
			# print(message)
			motor_speed = float(message[0])
			motor_diff = float(message[1])
			direction = message[2]
			motor_slow = motor_speed - motor_diff
			scale = 0.96 #Taken from trials
			#Ensure that the motor speed doesn't exceed the max value
			if motor_speed < -1: 
				motor_speed = -1
			elif motor_speed > 1:
				motor_speed = 1
			if motor_slow < -1: 
				motor_slow = -1
			elif motor_slow > 1:
				motor_slow = 1
		    # motor 4 is left, motor 1 is right
			# print('speed', motor_speed, 'motor slow:', motor_slow, 'direction:', direction)
			if direction == 'S' or direction == 'F' or direction == 'B':
				# print('direction is S or F or B')
				kit.motor4.throttle = motor_speed
				kit.motor1.throttle = motor_speed * scale 
			elif direction == 'L': #turning left
				# print('direction is Left')
				kit.motor4.throttle = motor_slow
				kit.motor1.throttle = motor_speed * scale
			elif direction == 'R': #turning right
				# print('direction is Right')
				kit.motor4.throttle = motor_speed 
				kit.motor1.throttle = motor_slow * scale
			msg = [motor_speed, motor_diff]
			# Wait for queue to be empty
			if child_conn.empty():
				#Put msg into queue
				child_conn.put(msg)
	except KeyboardInterrupt:
		kit.motor4.throttle = 0
		sock.close()
		
if __name__ == '__main__':
	control()


