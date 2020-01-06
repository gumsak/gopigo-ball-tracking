# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import argparse
import cv2
import imutils
import time

from multiprocessing.pool import ThreadPool
from multiprocessing import Process
import multiprocessing as multip

#import gopigo

# Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.
#gpg = gopigo3.GoPiGo3()

robot_is_moving = False
robot_is_turning = False

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
def __move_robot__(radius, center, w, pipe_in):
    
    #print("Moving robot... Radius", radius)
    
    global robot_is_moving, robot_is_turning
                  
    # start moving toward the object if it is far & the robot isn't moving
    if(radius < 100) and check_object_centered(center, w):
        #print("Should move...")
        if not robot_is_moving:# and not robot_is_turning:
            #pipe_in.send("forward")
            robot_is_moving = True
            __move_forward__()
        
    # stop moving if close enough of the object & the robot is moving
    elif (radius >= 100) or not check_object_centered(center, w):
        #print("Is getting close...")

        if robot_is_moving or robot_is_turning:
            print("Should stop...")
            #gpg.stop()
            #pipe_in.send("stop")
            robot_is_moving = False

# set the robot's movements
#radius, center, w
def control_robot(radius, center, w):
    __turn_robot__(center[0], 600)
    #__move_robot__(radius, center, 600)

def set_movement(pipe_out):
        
    #global robot_is_moving

    command = pipe_out.recv()
    
    print('Pipe out process...')#, command

    if command == "forward":
        print("forward...")
        #robot_is_moving = True
        #gpg.right()
    elif command == "reverse":
        print("reverse...")
        #robot_is_moving = True
        #gpg.right()
    elif command == "left":
        print("turn left...")
        #robot_is_moving = True
        #gpg.right()
    elif command == "right":
        print("turn right...")
        #robot_is_moving = True
        #gpg.right()
    elif command == "stop":
        print("Stopping...")
        #robot_is_moving = False
        #gpg.stop()
    else:
        print("Stopping...")
        #robot_is_moving = False
        #gpg.stop()
        
    pipe_out.close
    
#set up the parallel processing: param1 = pipe, param2 = function to parallelize
def init_multiprocessing(pipe_out, func):
    
    robot_process = Process(name = 'robot_controller',
                            target = func,
                            args = (pipe_out,))
    
    print("Creating process:", robot_process.name)
    
    return robot_process

# define the lower and upper boundaries of the possible colors of the 
# ball in the HSV color space, then initialize the list of tracked points
# hsv color picking example: https://stackoverflow.com/a/48367205
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

blueLower = (110, 140, 50)
blueUpper = (125, 255, 255)

orangeLower = (10, 100, 20)
orangeUpper = (25, 255, 255)

pts = deque(maxlen=args["buffer"])

# allow the camera or video file to warm up
time.sleep(2.0)

if __name__ == '__main__':

    #global robot_is_moving, robot_is_turning
    
    # create the pipes used for the communication between 2 process
    parent_p, child_p = multip.Pipe()
    
    # start processing
    #robot_process = init_multiprocessing(child_p, set_movement)
    robot_process = Process(name = 'robot_controller',
                            target = set_movement,
                            args = (child_p,))
    
    #robot_process.start()

    w = 600

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
            # its center
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            
            #get the ceter of the video
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            #print("center = " + str(center))
            
            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and its center on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                    (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                
                # check if the robot is already in motion
                #if robot_is_moving || robot_is_turning:
                #    if(radius >= 100) and check_object_centered(center, w):
                        
                #else:
                    #parent_p.send()
                    #__turn_robot__(center[0], 600)
                try:
                    __move_robot__(radius, center[0], w, parent_p)
                except:
                    pass
    
        # display the frame on the screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
    
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

# close process & pipes
robot_process.join()
robot_process.close()
parent_p.close()
child_p.close()
          
if robot_process.is_alive:
    print('{} process still alive...'.format(robot_process.name))
else:
    print('{} process stoped...'.format(robot_process.name))

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()

# otherwise, release the camera
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()     