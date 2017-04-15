#!/usr/bin/env python
import cv2
import urllib 
import numpy as np
from sensor_msgs.msg import Image 
import roslib
import sys
import rospy
import cv
from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError 
import argparse

class IPCamera(object):
    def __init__(self, url):
	rospy.logerr('trying to get url ')
        try:
            self.stream=urllib.urlopen(url)
        except:
            rospy.logerr('Unable to open camera stream: ' + str(url))
            sys.exit() #'Unable to open camera stream')
	rospy.logerr('got the url!!! ')
        self.bytes=''
        self.image_pub = rospy.Publisher("camera_image", Image)
        self.bridge = CvBridge()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='ip_camera.py', description='reads a given url string and dumps it to a ros_image topic')
    parser.add_argument('-g', '--gui', action='store_true', help='show a GUI of the camera stream')
    #define your IP Camera URL in here. My Camera is using Belkin Camera, which is using this address to access the images
    #or you can type in your command like this: $python ip_camera -u YOUR_CAMERA_URL -g
    parser.add_argument('-u', '--url', default='http://10.42.0.40:8080/mjpegfeed?320x240', help='camera stream url to parse')
    args = parser.parse_args()
    
    rospy.init_node('IPCamera', anonymous=True)
    ip_camera = IPCamera(args.url)
    rospy.logerr('all set going into loop :)')
    while not rospy.is_shutdown():
        ip_camera.bytes += ip_camera.stream.read(1024)
        a = ip_camera.bytes.find('\xff\xd8')
        b = ip_camera.bytes.find('\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = ip_camera.bytes[a:b+2]
            ip_camera.bytes= ip_camera.bytes[b+2:]
            i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
            image_message = cv.fromarray(i)
	    cv2.imshow('video', i)
            image_message = np.asarray(image_message[:,:])
            ip_camera.image_pub.publish(ip_camera.bridge.cv2_to_imgmsg(image_message, "bgr8"))

            if args.gui:
                cv2.imshow('IP Camera Publisher Cam',i)
            if cv2.waitKey(1) ==27: # wait until ESC key is pressed in the GUI window to stop it
                exit(0) 
