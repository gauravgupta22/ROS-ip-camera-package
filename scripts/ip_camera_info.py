import cv2
import numpy as np
import rospy
from sensor_msgs.msg import CameraInfo, Image
import time
import yaml

def parse_calibration_yaml(calib_file):
    with file(calib_file, 'r') as f:
        params = yaml.load(f)

    cam_info = CameraInfo()
    cam_info.height = params['image_height']
    cam_info.width = params['image_width']
    cam_info.distortion_model = params['distortion_model']
    cam_info.K = params['camera_matrix']['data']
    cam_info.D = params['distortion_coefficients']['data']
    cam_info.R = params['rectification_matrix']['data']
    cam_info.P = params['projection_matrix']['data']

    return cam_info


def publish_stereo_sequence(left_cam_info,left_cam_pub):
    #use the current time as message time stamp for all messages
    stamp = rospy.Time.from_sec(time.time())
    left_cam_info.header.stamp = stamp

    #publish the camera info messages first
    left_cam_pub.publish(left_cam_info)

    rospy.sleep(1.0)

if __name__ == '__main__':
    import argparse
    import glob

    parser = argparse.ArgumentParser(description='Publish a a sequence of stereo images.')
    parser.add_argument('-cl', help='The left camera calibration parameters file', dest='left_calib',
                        metavar='calibration yaml file', required=True)
    args = parser.parse_args()
    left_cam_info = parse_calibration_yaml(args.left_calib)
    left_cam_pub = rospy.Publisher('/camera_ip_info', CameraInfo)
    rospy.init_node('stereo_pub')

    try:
        while not rospy.is_shutdown():
            publish_stereo_sequence(left_cam_info, left_cam_pub)            
            rospy.sleep(1.0)

    except rospy.ROSInterruptException:
        pass
