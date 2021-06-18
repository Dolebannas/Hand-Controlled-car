import socket
import time
import board
from adafruit_motorkit import MotorKit
from flask import Flask, render_template, Response
import cv2 
import threading

UDP_IP 	= "192.168.1.114"
UDP_PORT = 5005
kit = MotorKit(i2c=board.I2C())
sock = socket.socket(socket.AF_INET, # Internet
	                     socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UDP_IP, UDP_PORT))

app = Flask(__name__)

cap = cv2.VideoCapture(0)

# def gen():
# 	cap = cv2.VideoCapture(0)
#     # Read until video is completed
# 	while(cap.isOpened()):
#       	# Capture frame-by-frame
# 		ret, img = cap.read()
# 		if ret == True:
# 			img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
# 			img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 			frame = cv2.imencode('.jpg', img)[1].tobytes()
# 			yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
# 		else: 
# 			break

def main():
	try:
		while True:
			ret, img = cap.read()
			if ret == True:
				img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
				img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				frame = cv2.imencode('.jpg', img)[1].tobytes()
				gen = (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
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
			# a = min(value, threshold_top) # to limit the top
			# a = max(value, threshold_bot) # to limit the bottom
			if motor_speed < -1: 
				motor_speed = -1
			elif motor_speed > 1:
				motor_speed = 1
			if motor_slow < -1: 
				motor_slow = -1
			elif motor_slow > 1:
				motor_slow = 1
		    # motor 4 is left, motor 1 is right
			print('speed', motor_speed, 'motor slow:', motor_slow, 'direction:', direction)
			if direction == 'S' or direction == 'F' or direction == 'B':
				print('direction is S or F or B')
				kit.motor4.throttle = motor_speed
				kit.motor1.throttle = motor_speed * scale 
			elif direction == 'L': #turning left
				print('direction is Left')
				kit.motor4.throttle = motor_slow
				kit.motor1.throttle = motor_speed * scale
			elif direction == 'R': #turning right
				print('direction is Right')
				kit.motor4.throttle = motor_speed 
				kit.motor1.throttle = motor_slow * scale	
	except KeyboardInterrupt:
		kit.motor4.throttle = 0
		kit.motor1.throttle = 0
		sock.close()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/video_feed')
def video_feed():	
	return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')

app.run(debug = True, host = '0.0.0.0')
