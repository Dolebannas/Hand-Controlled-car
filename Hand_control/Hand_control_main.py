import socket
from imu import MPU
import time
import csv

def main():

	UDP_IP = "192.168.1.114"
	UDP_PORT = 5005
	print("UDP target IP: %s" % UDP_IP)
	print("UDP target port: %s" % UDP_PORT)
	# Set up class
	gyro = 250 # 250, 500, 0, 2000 [deg/s]
	acc = 2 # 2, 4, 7, 16 [g]
	tau = 0.98	# k value, compensation and sensor weight
	mpu = MPU (gyro, acc, tau) # Initialize IMU object

	# Set up sensor and calibrate gyro with N points
	mpu.setUp()
	mpu.calibrateGyro(500)
	# Open socket for internet connection and UDP transmition
	sock = socket.socket(socket.AF_INET, # Internet
	socket.SOCK_DGRAM) # UDP
	# initalize ranges and thresholds
	front_thresh = 35
	back_thresh = 55
	left_thresh = -20
	right_thresh = 20
	front_range = front_thresh - 0
	back_range = 90 - back_thresh
	right_range = 60 - right_thresh 
	left_range = -60 - left_thresh
	base_speed = 0.5

	while True:
		mpu.compFilter()
		# Checks if the hand is between the back and front thresholds
		if front_thresh < mpu.roll < back_thresh and left_thresh < mpu.pitch <right_thresh:
			motor_speed = 0
			motor_diff = 0
			direction = "S"
		elif mpu.roll < front_thresh: # checks if hand has passed the front treshold
			motor_speed = (((front_thresh - mpu.roll)/front_range)*(1-base_speed)) + base_speed
			if left_thresh < mpu.pitch < right_thresh:
				motor_diff = 0
				direction = "F"
			elif mpu.pitch > right_thresh: # checks if hand has passed the right threshold
				motor_diff = (mpu.pitch - right_thresh)/right_range 
				direction = "R"
			elif mpu.pitch < left_thresh: # checks if hand has passed the left threshold
				motor_diff = (mpu.pitch - left_thresh)/left_range 
				direction = "L" 
		elif mpu.roll > back_thresh: # checks if hand has passed the back treshold
			motor_speed = (((mpu.roll - back_thresh)/back_range)*(-1 + base_speed)) - base_speed
			if left_thresh < mpu.pitch < right_thresh: #checks if hand has passed the left threshold
				motor_diff = 0
				direction = "B"
			elif mpu.pitch > right_thresh: # checks if hand has passed the right threshold
				motor_diff = -(mpu.pitch - right_thresh)/right_range 
				direction = "R"
			elif mpu.pitch < left_thresh: # checks if hand has passed the left threshold
				motor_diff = -(mpu.pitch - left_thresh)/left_range 
				direction = "L"
		# round data to two decimal points
		motor_speed = round(motor_speed,2) 
		motor_diff = round(motor_diff,2)
		# convert imformation to combined string
		message = str(motor_speed) + '_' + str(motor_diff) + '_' + direction #leftforwards
		printmsg = ("motor speed: {}, motor_diff: {}, direction {}".format(round(motor_speed,2),round(motor_diff,2),direction))
		print(printmsg)
		# Send information as byte over UDP socket
		sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
# Main loop
if __name__ == '__main__':
	main()