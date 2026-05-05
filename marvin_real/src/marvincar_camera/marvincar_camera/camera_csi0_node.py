#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class CameraCSI0Node(Node):
    def __init__(self):
        super().__init__('camera_csi0_node')

        self.bridge = CvBridge()
        self.publisher = self.create_publisher(Image, '/marvin/camera/csi0/image_raw', 10)

        # GStreamer pipeline para CSI0
        self.gst_pipeline = (
            'nvarguscamerasrc sensor-id=0 ! '
            'video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1 ! '
            'nvvidconv ! video/x-raw,format=BGRx ! '
            'videoconvert ! video/x-raw,format=BGR ! '
            'appsink'
        )

        self.cap = cv2.VideoCapture(self.gst_pipeline, cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            self.get_logger().error('Failed to open CSI0 camera')
            return

        self.get_logger().info('CSI0 camera initialized')

        # Timer para capturar frames
        self.timer = self.create_timer(0.033, self.capture_frame)  # ~30 FPS

    def capture_frame(self):
        ret, frame = self.cap.read()

        if ret:
            msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            msg.header.frame_id = 'camera_csi0'
            self.publisher.publish(msg)
        else:
            self.get_logger().warn('Failed to capture frame from CSI0')

    def destroy_node(self):
        if self.cap:
            self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = CameraCSI0Node()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
