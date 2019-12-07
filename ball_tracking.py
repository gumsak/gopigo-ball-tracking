# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

#import gopigo3

# Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.
#gpg = gopigo3.GoPiGo3()

#possibility to use the easygopigo3 lib
# importing the EasyGoPiGo3 class
#from easygopigo3 import EasyGoPiGo3
# instantiating a EasyGoPiGo3 object
#GPG = EasyGoPiGo3()

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    vs = VideoStream(src=0).start()
    
# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

#time.sleep(2)
#width and height of the screen
#width = vs.get(cv2.CAP_PROP_FRAME_WIDTH)
#height = vs.get(cv2.CAP_PROP_FRAME_HEIGHT)

#move the robot forward
def __move_forward__():
    #gpg.forward()
    print("Moving forward")

#move the robot backward
def __move_backward__():
    #gpg.backward
    print("Reversing")

    
#move the robot left
def __turn_left__():
    #gpg.left()
    print("Left turn")

#move the robot right
def __turn_right__():
    #gpg.right()
    print("Right turn")

#check if the object is somewhat in the center of the view
def check_object_centered(objectCenter, w):
    if(objectCenter < (w/2)+20) and (objectCenter > (w/2)-20):
        return True
    else:
        return False
    
#turn the robot left or right
def __turn_robot__(objectCenter, w):
    #the object is on the right of the screen
    if(objectCenter > (w/2)+20):
        __turn_right__()
        
    #the object is on the lrft of the screen
    if(objectCenter < (w/2)-20):
        __turn_left__()
        
    else:
        #gpg.stop()
        print("Stopping")

#move the robot forward/backward
def __move_robot__(radius, center, w):
    if(radius < 100) and check_object_centered(center, w):
       __move_forward__()
    else:
       #gpg.stop()
       print("Stopping")

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

blueLower = (110, 140, 50)
blueUpper = (125, 255, 255)

pts = deque(maxlen=args["buffer"])

# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping
while True:
    # grab the current frame
    frame = vs.read()
 
    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame
 
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break
 
    # resize the frame, blur it, and convert it to the HSV
    # color space
    #frame = imutils.resize(frame, width=600)
    #blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        print("center = " + str(center))
        
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            __turn_robot__(center[0], 600)
            __move_robot__(radius, center, 600)

#    # update the points queue
#    pts.appendleft(center)
#
#    # loop over the set of tracked points
#    for i in range(1, len(pts)):
#        # if either of the tracked points are None, ignore
#        # them
#        if pts[i - 1] is None or pts[i] is None:
#            continue
#
#        # otherwise, compute the thickness of the line and
#        # draw the connecting lines
#        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
#        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()

# otherwise, release the camera
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()