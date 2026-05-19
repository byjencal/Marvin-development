import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class MarvinStereoCamera(Node):
    def __init__(self):
        super().__init__('marvin_stereo_camera')
        
        # Publicadores para ambas cámaras
        self.pub_left = self.create_publisher(Image, 'camera_left/image_raw', 10)
        self.pub_right = self.create_publisher(Image, 'camera_right/image_raw', 10)
        
        # Frecuencia de publicación (~30 FPS)
        self.timer = self.create_timer(0.033, self.timer_callback)
        self.bridge = CvBridge()

        # Generar pipelines para los puertos CSI 0 y 1
        pipe_left = self.gstreamer_pipeline(sensor_id=0)
        pipe_right = self.gstreamer_pipeline(sensor_id=1)

        # Iniciar captura de video indicando que usamos GStreamer
        self.get_logger().info('Inicializando cámaras IMX219...')
        self.cap_left = cv2.VideoCapture(pipe_left, cv2.CAP_GSTREAMER)
        self.cap_right = cv2.VideoCapture(pipe_right, cv2.CAP_GSTREAMER)
    
    def gstreamer_pipeline(self, sensor_id, width=1280, height=720, framerate=60):
        # ¡Añadimos sensor-mode=4 para obligar a la Jetson a usar el modo de 60fps!
        return (
            f"nvarguscamerasrc sensor-id={sensor_id} sensor-mode=4 ! "
            f"video/x-raw(memory:NVMM), width={width}, height={height}, format=(string)NV12, framerate=(fraction){framerate}/1 ! "
            f"nvvidconv ! video/x-raw, format=(string)BGRx ! "
            f"videoconvert ! video/x-raw, format=(string)BGR ! "
            f"appsink drop=true max-buffers=1"
        )

    def timer_callback(self):
        # Leer frames de hardware
        ret_l, frame_l = self.cap_left.read()
        ret_r, frame_r = self.cap_right.read()

        # Convertir a formato ROS 2 y publicar
        if ret_l:
            msg_left = self.bridge.cv2_to_imgmsg(frame_l, encoding="bgr8")
            msg_left.header.frame_id = "camera_left_link"
            self.pub_left.publish(msg_left)
            
        if ret_r:
            msg_right = self.bridge.cv2_to_imgmsg(frame_r, encoding="bgr8")
            msg_right.header.frame_id = "camera_right_link"
            self.pub_right.publish(msg_right)

def main(args=None):
    rclpy.init(args=args)
    stereo_node = MarvinStereoCamera()
    
    try:
        rclpy.spin(stereo_node)
    except KeyboardInterrupt:
        pass
    finally:
        stereo_node.cap_left.release()
        stereo_node.cap_right.release()
        stereo_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()