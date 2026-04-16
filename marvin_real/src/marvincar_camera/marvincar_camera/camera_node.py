#!/usr/bin/env python3
# encoding: utf-8

"""
Camera node for MARVIN robot
Captures video from CSI cameras using GStreamer and publishes as ROS2 Image messages
"""

import cv2
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import rclpy


class CameraNode(Node):
    """ROS2 node that captures video from CSI cameras and publishes frame data"""

    def __init__(self, name):
        super().__init__(name)

        # Declare parameters
        self.declare_parameter('camera_0_id', 0)
        self.declare_parameter('camera_1_id', 1)
        self.declare_parameter('fps', 30)
        self.declare_parameter('width', 640)
        self.declare_parameter('height', 480)
        self.declare_parameter('camera_0_frame_id', 'camera_0')
        self.declare_parameter('camera_1_frame_id', 'camera_1')

        # Get parameters
        self.camera_0_id = self.get_parameter('camera_0_id').get_parameter_value().integer_value
        self.camera_1_id = self.get_parameter('camera_1_id').get_parameter_value().integer_value
        self.fps = self.get_parameter('fps').get_parameter_value().integer_value
        self.width = self.get_parameter('width').get_parameter_value().integer_value
        self.height = self.get_parameter('height').get_parameter_value().integer_value
        self.camera_0_frame_id = self.get_parameter('camera_0_frame_id').get_parameter_value().string_value
        self.camera_1_frame_id = self.get_parameter('camera_1_frame_id').get_parameter_value().string_value

        self.get_logger().info(f"Camera 0 ID: {self.camera_0_id}")
        self.get_logger().info(f"Camera 1 ID: {self.camera_1_id}")
        self.get_logger().info(f"Resolution: {self.width}x{self.height}")
        self.get_logger().info(f"FPS: {self.fps}")

        # Initialize CvBridge
        self.bridge = CvBridge()

        # Initialize OpenCV captures with GStreamer pipeline for Jetson CSI cameras
        self.cap_0 = None
        self.cap_1 = None

        # GStreamer pipeline for Jetson CSI camera
        gst_pipeline_0 = self._create_gst_pipeline(self.camera_0_id)
        gst_pipeline_1 = self._create_gst_pipeline(self.camera_1_id)

        # Try to open camera 0
        try:
            self.cap_0 = cv2.VideoCapture(gst_pipeline_0, cv2.CAP_GSTREAMER)
            if not self.cap_0.isOpened():
                self.get_logger().warn(f"Failed to open camera 0 (ID: {self.camera_0_id})")
            else:
                self.get_logger().info(f"Opened camera 0: {self.camera_0_id}")
        except Exception as e:
            self.get_logger().error(f"Error opening camera 0: {e}")

        # Try to open camera 1
        try:
            self.cap_1 = cv2.VideoCapture(gst_pipeline_1, cv2.CAP_GSTREAMER)
            if not self.cap_1.isOpened():
                self.get_logger().warn(f"Failed to open camera 1 (ID: {self.camera_1_id})")
            else:
                self.get_logger().info(f"Opened camera 1: {self.camera_1_id}")
        except Exception as e:
            self.get_logger().error(f"Error opening camera 1: {e}")

        # Create publishers
        self.image_pub_0 = self.create_publisher(Image, '/camera_0/image_raw', 10)
        self.image_pub_1 = self.create_publisher(Image, '/camera_1/image_raw', 10)

        # Create timer for publishing
        timer_period = 1.0 / self.fps
        self.timer = self.create_timer(timer_period, self.publish_frames)

    def _create_gst_pipeline(self, camera_id):
        """Create GStreamer pipeline for Jetson CSI camera"""
        return (
            f"nvarguscamerasrc sensor-id={camera_id} ! "
            f"video/x-raw(memory:NVMM), width={self.width}, height={self.height}, "
            f"format=NV12, framerate={self.fps}/1 ! "
            f"nvvidconv ! video/x-raw, format=BGRx ! "
            f"videoconvert ! video/x-raw, format=BGR ! appsink"
        )

    def publish_frames(self):
        """Capture and publish frames from both cameras"""

        # Camera 0
        if self.cap_0 and self.cap_0.isOpened():
            ret_0, frame_0 = self.cap_0.read()
            if ret_0:
                try:
                    msg_0 = self.bridge.cv2_to_imgmsg(frame_0, encoding="bgr8")
                    msg_0.header.frame_id = self.camera_0_frame_id
                    msg_0.header.stamp = self.get_clock().now().to_msg()
                    self.image_pub_0.publish(msg_0)
                except Exception as e:
                    self.get_logger().error(f"Error converting frame from camera 0: {e}")
            else:
                self.get_logger().warn("Failed to capture frame from camera 0")

        # Camera 1
        if self.cap_1 and self.cap_1.isOpened():
            ret_1, frame_1 = self.cap_1.read()
            if ret_1:
                try:
                    msg_1 = self.bridge.cv2_to_imgmsg(frame_1, encoding="bgr8")
                    msg_1.header.frame_id = self.camera_1_frame_id
                    msg_1.header.stamp = self.get_clock().now().to_msg()
                    self.image_pub_1.publish(msg_1)
                except Exception as e:
                    self.get_logger().error(f"Error converting frame from camera 1: {e}")
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
    camera_node.destroy_node()
    rclpy.shutdown()

