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

# Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.
#gpg = gopigo3.GoPiGo3()
from gopigo import * #Has the basic functions for controlling the GoPiGo Robot

robot_is_moving = False
robot_is_turning = False

robot_speed = 127

#possibility to use the easygopigo3 lib
# importing the EasyGoPiGo3 class
#from easygopigo3 import EasyGoPiGo3
# instantiating a EasyGoPiGo3 object
#gpg = EasyGoPiGo3()

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
    video_stream = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
    video_stream = cv2.VideoCapture(args["video"])

#time.sleep(2)
#width and height of the screen
#width = video_stream.get(cv2.CAP_PROP_FRAME_WIDTH)
#height = video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT)

#move the robot forward
def __move_forward__():
    #gpg.forward()
    #fwd()
    motor1(1,127)	
    motor2(1,127)	
    print("Moving forward")

#move the robot backward
def __move_backward__():
    #gpg.backward
    bwd()
    print("Reversing")

#move the robot left
def __turn_left__():
    #gpg.left()
    left()
    print("Left turn")

#move the robot right
def __turn_right__():
    #gpg.right()
    right()
    print("Right turn")

#stop both motors
def __stop_motors():
    motor1(1,0)
    motor2(1,0)
    
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
    '''    
    else:
        #gpg.stop()
        stop()
        print("Stopping")
    '''
#move the robot forward/backward
def __move_robot__(radius, center, w, pipe_in):
    
    #print("Moving robot... Radius", radius)
    global robot_is_moving, robot_is_turning
        
    print('moving', robot_is_moving)
    print('turning', robot_is_turning)

    # start moving toward the object if it is far & the robot isn't moving
    #if the object is far
    if(radius < 150):
        #and the object is centered
        if check_object_centered(center, w):
            print("Should move...")
            if robot_is_turning:
                robot_is_turning = False
                stop()
            #move toward it if not already doing so
            if not robot_is_moving and not robot_is_turning:
                #pipe_in.send("forward")
                robot_is_moving = True
                __move_forward__()
                
        #the object is not centered
        else:
            if robot_is_moving:
                robot_is_moving = False
                stop()
            #turn toward it if not already moving
            if not robot_is_moving and not robot_is_turning:
                #pipe_in.send("forward")
                robot_is_turning = True
                __turn_robot__(center, w)
                
    else:
        if check_object_centered(center, w):
            robot_is_moving = False
            robot_is_turning = False
            stop()
        #the object is not centered
        else:
            if robot_is_moving:
                robot_is_moving = False
                stop()
            #turn toward it if not already moving
            if not robot_is_moving and not robot_is_turning:
                #pipe_in.send("forward")
                robot_is_turning = True
                __turn_robot__(center, w) 

# set the robot's movements
#radius, center, w
def control_robot(radius, object_center, w):
    
    #print("Moving robot... Radius", radius)
    global robot_is_moving, robot_is_turning
        
    print('radius', radius)
    
    center_left_anchor = (w/2) - 20
    center_right_anchor = (w/2) + 20
    center_to_border = w/2 +40
    
    #motor1(1,robot_speed)
    #motor2(1,robot_speed)
    
    #object is on the left
    #if center < center_left_anchor and objectCenter > center_right_anchor:
    if(radius < 225):
        
        if object_center < center_left_anchor:
            motor2_speed = center_left_anchor - object_center + robot_speed
            motor1_speed = 1 + robot_speed
        elif object_center > center_right_anchor:
            motor1_speed = object_center - center_right_anchor + robot_speed
            motor2_speed = 1 + robot_speed
        else:
            motor1_speed = 220 + robot_speed
            motor2_speed = 220 + robot_speed
            
        print('object center', object_center)
        

        print('left_anch {}, right_anch {}'.format(motor1_speed,
                                                  motor2_speed))
        if motor1_speed >= 255:
            motor1_speed = 255
        if motor2_speed >= 255:
            motor2_speed = 255
       
        print('mot1 {}, mot2 {}'.format(motor1_speed, motor2_speed))

        motor2(1,int(motor1_speed))
        motor1(1,int(motor2_speed))
        
    else:
        stop()
    # start moving toward the object if it is far & the robot isn't moving
    #if the object is far

# define the lower and upper boundaries of the possible colors of the 
# ball in the HSV color space, then initialize the list of tracked points
# hsv color picking example: https://stackoverflow.com/a/48367205
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

blueLower = (110, 140, 50)
blueUpper = (125, 255, 255)

orangeLower = (10, 100, 20)
orangeUpper = (25, 255, 255)

redLower = (160, 120, 20)
redUpper = (180, 255, 255)

lowHue = 160
highHue = 180
lowSat = 120
highSat = 255
lowVal = 20
highVal = 255


pts = deque(maxlen=args["buffer"])

# allow the camera or video file to warm up
time.sleep(2.0)

if __name__ == '__main__':

    #global robot_is_moving, robot_is_turning

    # create the pipes used for the communication between 2 process
    parent_p, child_p = multip.Pipe()
    
    # start processing
    #robot_process = init_multiprocessing(child_p, set_movement)
    
    #robot_process.start()

    w = 640
    
    shape = 'none'
    
    #fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    #video_record = cv2.VideoWriter('video.avi', fourcc, 20, (640, 480))
    
    # keep looping
    while True:
        # grab the current frame
        frame = video_stream.read()
     
        # handle the frame from VideoCapture or VideoStream
        frame = frame[1] if args.get("video", False) else frame
     
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if frame is None:
            break
     
        #flip the image (the gopigo camera is physically flip, so we
        #have to flip it in the program to have a normal image)
        frame = cv2.flip(frame, -1)
        #img = cv2.flip(frame, -1)
        
        # resize the frame, blur it, and convert it to the HSV
        # color space
        #frame = imutils.resize(frame, width=600)
        #blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     
        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, redLower, redUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnt = imutils.grab_contours(cnts)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        center = None
        
        # only proceed if at least one contour was found
        if len(cnt) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # its center
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            
            peri = cv2.arcLength(cnts[0], True)
            approx = cv2.approxPolyDP(cnts[0], 0.04 * peri, True)
            #print('poly', approx)
            print('size-length', len(approx))
            
            #get the center of the video
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            #print("center = " + str(center))
            
            # only proceed if the radius meets a minimum size
            if len(approx) > 4:
                print('in approx')
                if radius > 10:
                
                    # draw the circle and its center on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                        (0, 255, 255), 2)
                    #cv2.circle(frame, center, 5, (0, 0, 255), -1)
                
                    try:
                        control_robot(radius, center[0], w)
                    except:
                        print('exception error')
            else:
                pass
                #stop()
        
        #if no object is detected stop the robot
        else:
            robot_is_moving = False
            robot_is_turning = False
            stop()
            #left()
            
        # display the frame on the screen
        cv2.imshow("Frame", frame)
        
        key = cv2.waitKey(1) & 0xFF
    
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

# close process & pipes
parent_p.close()
child_p.close()
          
stop()          

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    video_stream.stop()

# otherwise, release the camera
else:
    video_stream.release()
    #video_record.release()
    
# close all windows
cv2.destroyAllWindows()     
