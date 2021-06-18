import time
import cv2
import numpy as np
from flask import Flask, render_template, Response
import Vehicle_control_main
import multiprocessing as mp

# Define app as a flask application
app = Flask(__name__)
#app.route decorator used to tell flask which methods to call on at the given URL
@app.route('/')
def index():
	return render_template('index.html') #, data = data)

def gen():
	#Initialize camera capture reading from default camera
	cap = cv2.VideoCapture(0)
    # Read until video is completed
	while True:
		# Get item from queue
		motor_speed = q.get()
		print(motor_speed)
      	# Capture frame-by-frame
		ret, img = cap.read()
		if ret == True:
			img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
			# add text to webserver
			cv2.putText(img,'motor speed: ' + str(motor_speed), (25,25), cv2.FONT_HERSHEY_SIMPLEX, 0.6,(255, 0, 0),2, cv2.LINE_AA)
			frame = cv2.imencode('.jpg', img)[1].tobytes()
			# Yield's the frame as a byte and since yield is generator, new frame is generated each time
			yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
		else:
			break
			cap.release()
@app.route('/video_feed')
def video_feed():
	# Return camera frame to flask webserver
	return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
	try:
		# Open multiprocessing Queue
		q = mp.Queue()
		# Spawn vehicle_control_main.py, passing q as an arguement
		p = mp.Process(target=Vehicle_control_main.control, args=(q,))
		p.start()
		# Create web server with host ID 0.0.0.0 so foreign devices can access
		app.run(debug = False, host = '0.0.0.0', port = '5000')
	except KeyboardInterrupt:
		q.close()
		p.close()
		cap.release()