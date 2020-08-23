# import the necessary packages
from collections import deque
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import time
import atexit
import numpy as np
import argparse
import imutils
import cv2
import math

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
#greenLower = (29, 86, 6)
#greenUpper = (64, 255, 255)

#greenLower = (98, 109, 20) #blue
#greenUpper = (112, 255, 255) #blue

#greenLower = (5, 50, 50) #orange
#greenUpper = (15, 255, 255) #orange

greenLower = (160, 140, 50) #red
greenUpper = (179, 255, 255) #red

#sensitivity = 15
#greenLower = np.array([0, 0, 255-sensitivity])
#greenUpper = np.array([255, sensitivity, 255])

pts = deque(maxlen=args["buffer"])

mh = Adafruit_MotorHAT(addr=0x60)
frameCount = 0
def turnOffMotors():
	mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
atexit.register(turnOffMotors)

myMotor = mh.getMotor(3)
#clockwise == 1 is BACKWARD, 0 is FORWARD, -1 is not moving
clockwise = -1

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	camera = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
else:
	camera = cv2.VideoCapture(args["video"])

##fourcc = cv2.VideoWriter_fourcc(*'XVID')##
##out = cv2.VideoWriter('output.avi', fourcc, 20.0,(640,480))##

# keep looping
while True:
	# grab the current frame
	(grabbed, frame) = camera.read()

	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if args.get("video") and not grabbed:
		break
##	oframe = cv2.flip(frame,0)##
##	out.write(oframe)##


	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=600)
	cv2.imwrite('frame.jpg', frame)
	# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	cv2.imwrite('hsv.jpg', hsv)
	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	# erode and dilate to remove noise
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	cv2.imwrite('inRange.jpg', mask)
	mask = cv2.erode(mask, None, iterations=2)
	cv2.imwrite('erode.jpg', mask)
	mask = cv2.dilate(mask, None, iterations=2)
	cv2.imwrite('dilate.jpg', mask)
	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None
	
	if len(cnts) <= 0:
		myMotor.run(Adafruit_MotorHAT.RELEASE)

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		
		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
		
			mover=int(300-x)
			movel=int(x-300)
			frameCount = frameCount + 1
			print(int(x))
			if int(x) > 350:# and frameCount == 10:  #64:
#				while movel > 0:		
				frameCount = 0
				myMotor.run(Adafruit_MotorHAT.RELEASE)
				myMotor.run(Adafruit_MotorHAT.FORWARD)
				print "\tmoving camera left..."
				clockwise = 0
				#for i in range(movel):
				#	myMotor.setSpeed(i)
				#	time.sleep(0.01)
				#print "\tslow down..."
				#for i in reversed(range(movel)):
				#	myMotor.setSpeed(i)
				#	time.sleep(0.01)
				myMotor.setSpeed(255)
			elif int(x) < 250:# and frameCount == 10: #64
					
				frameCount = 0
				myMotor.run(Adafruit_MotorHAT.RELEASE)
				myMotor.run(Adafruit_MotorHAT.BACKWARD)
				print "\tmoving camera right.."
				clockwise = 1
				#for i in range(mover):
				#	myMotor.setSpeed(i)
				#	time.sleep(0.01)
				#print "\tslow down..."
				#for i in reversed(range(mover)):
				#	myMotor.setSpeed(i)
				#	time.sleep(0.01)
				myMotor.setSpeed(255)
			if x >= 250 and x<=350:
				myMotor.run(Adafruit_MotorHAT.RELEASE)
				#myMotor.setSpeed(0)
#		if radius > 100 and clockwise == 1:
#			myMotor.run(Adafruit_MotorHAT.RELEASE)
#			myMotor.run(Adafruit_MotorHAT.FORWARD)
#			print "\treached right edge moving camera counter-clockwise.."
#			clockwise = 0
#			myMotor.setSpeed(255)
#			time.sleep(0.1)
#		elif radius > 100 and clockwise == 0:
#			myMotor.run(Adafruit_MotorHAT.RELEASE)
#			myMotor.run(Adafruit_MotorHAT.BACKWARD)
#			print "\treached left edge moving camera clockwise.."
#			clockwise = 1
#			myMotor.setSpeed(255)
#			time.sleep(0.1)

	# update the points queue
	pts.appendleft(center)

	# loop over the set of tracked points
	for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)



	# show the frame to our screen
	cv2.imshow("Frame", frame)
	cv2.imwrite('final.jpg', frame)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
##out.release()##
cv2.destroyAllWindows()
