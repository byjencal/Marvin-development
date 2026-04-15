#!/usr/bin/env python3
# encoding: utf-8

"""
Camera node for MARVIN robot
Captures video from USB cameras and publishes as ROS2 Image messages
"""

import cv2
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Header
import rclpy


class CameraNode(Node):
    """ROS2 node that captures video from USB cameras and publishes frame data"""

    def __init__(self, name):
        super().__init__(name)

        # Declare parameters
        self.declare_parameter('camera_0_device', '/dev/video0')
        self.declare_parameter('camera_1_device', '/dev/video1')
        self.declare_parameter('fps', 30)
        self.declare_parameter('camera_0_frame_id', 'camera_0')
        self.declare_parameter('camera_1_frame_id', 'camera_1')

        # Get parameters
        self.camera_0_device = self.get_parameter('camera_0_device').get_parameter_value().string_value
        self.camera_1_device = self.get_parameter('camera_1_device').get_parameter_value().string_value
        self.fps = self.get_parameter('fps').get_parameter_value().integer_value
        self.camera_0_frame_id = self.get_parameter('camera_0_frame_id').get_parameter_value().string_value
        self.camera_1_frame_id = self.get_parameter('camera_1_frame_id').get_parameter_value().string_value

        self.get_logger().info(f"Camera 0 device: {self.camera_0_device}")
        self.get_logger().info(f"Camera 1 device: {self.camera_1_device}")
        self.get_logger().info(f"FPS: {self.fps}")

        # Initialize OpenCV captures
        self.cap_0 = None
        self.cap_1 = None
        self.seq_0 = 0
        self.seq_1 = 0

        try:
            self.cap_0 = cv2.VideoCapture(self.camera_0_device)
            if not self.cap_0.isOpened():
                self.get_logger().warn(f"Failed to open camera: {self.camera_0_device}")
            else:
                self.get_logger().info(f"Opened camera 0: {self.camera_0_device}")
        except Exception as e:
            self.get_logger().error(f"Error opening camera 0: {e}")

        try:
            self.cap_1 = cv2.VideoCapture(self.camera_1_device)
            if not self.cap_1.isOpened():
                self.get_logger().warn(f"Failed to open camera: {self.camera_1_device}")
            else:
                self.get_logger().info(f"Opened camera 1: {self.camera_1_device}")
        except Exception as e:
            self.get_logger().error(f"Error opening camera 1: {e}")

        # Create publishers
        self.image_pub_0 = self.create_publisher(Image, '/camera_0/image_raw', 10)
        self.image_pub_1 = self.create_publisher(Image, '/camera_1/image_raw', 10)

        # Create timer for publishing
        timer_period = 1.0 / self.fps
        self.timer = self.create_timer(timer_period, self.publish_frames)

    def cv2_to_ros_image(self, cv_image, frame_id, seq):
        """Convert OpenCV image to ROS2 Image message"""
        msg = Image()
        msg.header.seq = seq
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = frame_id

        # Image dimensions
        h, w = cv_image.shape[:2]
        msg.height = h
        msg.width = w

        # Encoding (BGR for OpenCV)
        msg.encoding = "bgr8"
        msg.is_bigendian = False
        msg.step = w * 3

        # Data (flatten and convert to bytes)
        msg.data = cv_image.tobytes()

        return msg

    def publish_frames(self):
        """Capture and publish frames from both cameras"""

        # Camera 0
        if self.cap_0 and self.cap_0.isOpened():
            ret_0, frame_0 = self.cap_0.read()
            if ret_0:
                self.seq_0 += 1
                msg_0 = self.cv2_to_ros_image(frame_0, self.camera_0_frame_id, self.seq_0)
                self.image_pub_0.publish(msg_0)
            else:
                self.get_logger().warn("Failed to capture frame from camera 0")

        # Camera 1
        if self.cap_1 and self.cap_1.isOpened():
            ret_1, frame_1 = self.cap_1.read()
            if ret_1:
                self.seq_1 += 1
                msg_1 = self.cv2_to_ros_image(frame_1, self.camera_1_frame_id, self.seq_1)
                self.image_pub_1.publish(msg_1)
            else:
                self.get_logger().warn("Failed to capture frame from camera 1")

    def __del__(self):
        """Clean up resources"""
        if self.cap_0:
            self.cap_0.release()
        if self.cap_1:
            self.cap_1.release()


def main():
    rclpy.init()
    camera_node = CameraNode('camera_node')
    rclpy.spin(camera_node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
