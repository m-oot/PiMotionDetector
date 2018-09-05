# USAGE
# python motion_detector.py
# python motion_detector.py --video videos/example_01.mp4

# import the necessary packages
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
#import sendEmail
import SendEmail2
from PIL import Image
import imagehash

# global variables
lastMotionDetectedTime = datetime.datetime.min
lastEmailSentTime = datetime.datetime.min
captureFrameTime = datetime.datetime.max
needFrameCaptured = True 
imageHash = None
sameHashCount = 0
lastHashTime = datetime.datetime.min
emailImageInterval = 15 #Time in seconds

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=600, help="minimum area size")
args = vars(ap.parse_args())

# if the video argument is None, then we are reading from piCam
if args.get("video", None) is None:
	print("Trying to get piCam VideoStream...")
	vs = VideoStream(src=0, usePiCamera=True, framerate=32).start()
	print("piCam VideoStream started.")
	time.sleep(2.0)

# otherwise, we are reading from a video file
else:
	vs = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None

# loop over the frames of the video
while True:
	# grab the current frame and initialize the occupied/unoccupied
	# text
	frame = vs.read()
	frame = frame if args.get("video", None) is None else frame[1]
	text = "Unoccupied"
	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if frame is None:
		print("Unable to grab frame.")
		break

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = gray		
		imageHash = imagehash.dhash(Image.fromarray(frame))
		lastHashTime = datetime.datetime.now()
		continue

	# compute the absolute difference between the current frame and
	# first frame
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 50, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue
		
		# checking if firstFrame needs to be replaced
		if((imageHash == imagehash.dhash(Image.fromarray(frame))) and ((datetime.datetime.now() - lastHashTime).seconds > 15)):		
			firstFrame = None
			print("First frame being replaced.")

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Occupied"
		currentTime = datetime.datetime.now()
		if(needFrameCaptured):
			captureFrameTime = currentTime + datetime.timedelta(seconds=2)
			needFrameCaptured = False 
		lastMotionDetectedTime = currentTime
		imageHash = imagehash.dhash(Image.fromarray(frame))
		
		#Update servo position

		#If servo position was updated update first frame
 
		#Facial Recognition will go here

		#Save image and send email if neccessary
		cv2.imwrite('SecurityCamMotionDetected.png', frame)
		if(((lastMotionDetectedTime - lastEmailSentTime).seconds > emailImageInterval) and (currentTime > captureFrameTime)):
			#sendEmail.send()
			SendEmail2.SendMail('SecurityCamMotionDetected.png')
			lastEmailSentTime = currentTime
			captureFrameTime = datetime.datetime.max
			needFrameCaptured = True
	# draw the text and timestamp on the frame
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# show the frame and record if the user presses a key
	cv2.imshow("Security Feed", frame)
	#cv2.imshow("Thresh", thresh)
	#cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
