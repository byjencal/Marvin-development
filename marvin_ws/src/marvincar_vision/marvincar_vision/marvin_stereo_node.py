import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
import cv2

class MarvinStereoCamera(Node):
    def __init__(self):
        super().__init__('marvin_stereo_camera')
        
        self.pub_left = self.create_publisher(CompressedImage, 'camera_left/image_raw/compressed', 10)
        self.pub_right = self.create_publisher(CompressedImage, 'camera_right/image_raw/compressed', 10)
        
        # Aumentamos ligeramente la frecuencia para intentar alcanzar 30 FPS reales
        self.timer = self.create_timer(0.033, self.timer_callback)
        self.bridge = CvBridge()

        # Generar pipelines (Ahora piden 640x480 para igualar el rendimiento de la OAK-D)
        pipe_left = self.gstreamer_pipeline(sensor_id=0, width=640, height=480)
        pipe_right = self.gstreamer_pipeline(sensor_id=1, width=640, height=480)

        self.get_logger().info('Inicializando cámaras IMX219 optimizadas...')
        self.cap_left = cv2.VideoCapture(pipe_left, cv2.CAP_GSTREAMER)
        self.cap_right = cv2.VideoCapture(pipe_right, cv2.CAP_GSTREAMER)
    
    def gstreamer_pipeline(self, sensor_id, width=640, height=480, framerate=30):
        # TRUCO DE HARDWARE: nvarguscamerasrc lee a máxima calidad (720p 60fps), 
        # pero usamos 'nvvidconv' para que la GPU de la Jetson redimensione la imagen a 640x480
        # antes de dársela a Python. Esto quita un peso inmenso de la CPU.
        return (
            f"nvarguscamerasrc sensor-id={sensor_id} sensor-mode=4 ! "
            f"video/x-raw(memory:NVMM), width=1280, height=720, format=(string)NV12, framerate=(fraction)60/1 ! "
            f"nvvidconv ! video/x-raw, width={width}, height={height}, format=(string)BGRx ! "
            f"videoconvert ! video/x-raw, format=(string)BGR ! "
            f"appsink drop=true max-buffers=1"
        )

    def timer_callback(self):
        # TRUCO DE SOFTWARE: En lugar de .read(), usamos .grab()
        # grab() solo le dice al sensor "toma la foto YA", pero no se queda esperando a decodificarla.
        # Al disparar ambas casi al mismo tiempo, simulamos un disparo en paralelo (Multithreading).
        self.cap_left.grab()
        self.cap_right.grab()

        # retrieve() es la parte que decodifica. Como ya ambas tomaron la foto, 
        # la decodificación es mucho más rápida.
        ret_l, frame_l = self.cap_left.retrieve()
        ret_r, frame_r = self.cap_right.retrieve()

        if ret_l:
            msg_left = self.bridge.cv2_to_compressed_imgmsg(frame_l, dst_format='jpg')
            msg_left.header.frame_id = "camera_left_link"
            self.pub_left.publish(msg_left)
            
        if ret_r:
            msg_right = self.bridge.cv2_to_compressed_imgmsg(frame_r, dst_format='jpg')
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