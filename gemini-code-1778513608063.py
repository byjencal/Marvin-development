#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

def gstreamer_pipeline(sensor_id=0, sensor_mode=0, capture_width=1920, capture_height=1080, framerate=20):
    pipeline = (
        f"nvarguscamerasrc sensor-id={sensor_id} sensor-mode={sensor_mode} ! "
        f"video/x-raw(memory:NVMM),width={capture_width},height={capture_height},framerate={framerate}/1,format=NV12 ! "
        "nvvidconv ! "
        "video/x-raw,format=BGRx ! "
        "videoconvert ! "
        "video/x-raw,format=BGR ! "
        "appsink"
    )
    return pipeline

class CSICameraNode(Node):
    def __init__(self):
        super().__init__('csi_camera_node')
        
        # 1. Declarar y obtener parámetros
        self.declare_parameter('sensor_id', 0)
        self.sensor_id = self.get_parameter('sensor_id').get_parameter_value().integer_value
        
        self.get_logger().info(f"Starting camera with sensor ID {self.sensor_id}")

        # 2. Configurar el publicador y el CvBridge
        topic_name = f'/csi_camera_{self.sensor_id}/image_raw'
        self.image_pub = self.create_publisher(Image, topic_name, 10)
        self.bridge = CvBridge()

        # 3. Inicializar la cámara con GStreamer
        pipeline = gstreamer_pipeline(sensor_id=self.sensor_id, sensor_mode=0)
        self.get_logger().info(f"GStreamer pipeline: {pipeline}")
        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            self.get_logger().error(f"Error: Unable to open camera with sensor ID {self.sensor_id}")
            return

        # 4. Crear un Timer para publicar a 20 Hz (1.0 / 20.0 = 0.05 segundos)
        timer_period = 0.05 
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().error(f"Error: Unable to read frame from camera with sensor ID {self.sensor_id}")
            return

        # Convertir el frame de OpenCV a mensaje de ROS 2
        image_msg = self.bridge.cv2_to_imgmsg(frame, "bgr8")
        # Establecer la estampa de tiempo actual del reloj de ROS 2
        image_msg.header.stamp = self.get_clock().now().to_msg()
        image_msg.header.frame_id = f"camera_{self.sensor_id}_frame"
        
        self.image_pub.publish(image_msg)

    def destroy_node(self):
        # Asegurarse de liberar la cámara al apagar el nodo
        if self.cap.isOpened():
            self.cap.release()
            self.get_logger().info("Camera released.")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    
    node = CSICameraNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Destruir el nodo explícitamente y apagar rclpy
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()