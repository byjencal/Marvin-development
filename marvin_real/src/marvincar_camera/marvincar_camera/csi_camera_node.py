#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


def gstreamer_pipeline(sensor_id=0, sensor_mode=0, capture_width=1920, capture_height=1080, framerate=20):
    """
    Construir un pipeline de GStreamer para nvarguscamerasrc.
    Compatible con Jetson Nano con cámaras IMX219 CSI.
    """
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
    """
    Nodo ROS2 para publicar imágenes de cámaras CSI (IMX219) en Jetson Nano.
    Parametrizables por sensor_id para soportar múltiples cámaras.
    """

    def __init__(self):
        super().__init__('csi_camera_node')

        # 1. Declarar y obtener parámetros
        self.declare_parameter('sensor_id', 0)
        self.declare_parameter('sensor_mode', 0)
        self.declare_parameter('capture_width', 1920)
        self.declare_parameter('capture_height', 1080)
        self.declare_parameter('framerate', 20)

        self.sensor_id = self.get_parameter('sensor_id').get_parameter_value().integer_value
        self.sensor_mode = self.get_parameter('sensor_mode').get_parameter_value().integer_value
        self.capture_width = self.get_parameter('capture_width').get_parameter_value().integer_value
        self.capture_height = self.get_parameter('capture_height').get_parameter_value().integer_value
        self.framerate = self.get_parameter('framerate').get_parameter_value().integer_value

        self.get_logger().info(
            f"Starting camera with sensor ID {self.sensor_id} - "
            f"Resolution: {self.capture_width}x{self.capture_height} @ {self.framerate}Hz"
        )

        # 2. Configurar el publicador y el CvBridge
        topic_name = f'/camera_{self.sensor_id}/image_raw'
        self.image_pub = self.create_publisher(Image, topic_name, 10)
        self.bridge = CvBridge()

        # 3. Inicializar la cámara con GStreamer
        pipeline = gstreamer_pipeline(
            sensor_id=self.sensor_id,
            sensor_mode=self.sensor_mode,
            capture_width=self.capture_width,
            capture_height=self.capture_height,
            framerate=self.framerate
        )
        self.get_logger().info(f"GStreamer pipeline: {pipeline}")

        try:
            self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        except Exception as e:
            self.get_logger().error(f"Exception creating VideoCapture: {str(e)}")
            return

        if not self.cap.isOpened():
            self.get_logger().error(
                f"Error: Unable to open camera with sensor ID {self.sensor_id}\n"
                f"  - Verify cámaras CSI are physically connected to Jetson Nano\n"
                f"  - Check: ls -la /dev/video*\n"
                f"  - Test: gst-launch-1.0 -v nvarguscamerasrc sensor-id={self.sensor_id} ! fakesink\n"
                f"  - Verify: dmesg | grep -i camera"
            )
            return

        self.get_logger().info(f"Camera {self.sensor_id} opened successfully")

        # 4. Crear un Timer para publicar a la frecuencia especificada
        timer_period = 1.0 / self.framerate
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        """Callback del timer para capturar y publicar frames."""
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().error(f"Error: Unable to read frame from camera with sensor ID {self.sensor_id}")
            return

        # Convertir el frame de OpenCV a mensaje de ROS 2
        image_msg = self.bridge.cv2_to_imgmsg(frame, "bgr8")

        # Establecer la estampa de tiempo actual del reloj de ROS 2
        image_msg.header.stamp = self.get_clock().now().to_msg()
        image_msg.header.frame_id = f"camera_{self.sensor_id}_optical_frame"

        # Publicar el mensaje
        self.image_pub.publish(image_msg)

    def destroy_node(self):
        """Liberar recursos de la cámara al apagar el nodo."""
        if self.cap.isOpened():
            self.cap.release()
            self.get_logger().info(f"Camera {self.sensor_id} released.")
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