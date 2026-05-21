import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
import cv2
import depthai as dai
import numpy as np

class MarvinOakDNode(Node):
    def __init__(self):
        super().__init__('marvin_oakd_node')
        
        # Publicadores comprimidos para cuidar el Wi-Fi
        self.pub_rgb = self.create_publisher(CompressedImage, 'oakd/color/image_raw/compressed', 10)
        self.pub_depth = self.create_publisher(CompressedImage, 'oakd/depth/image_raw/compressed', 10)
        self.bridge = CvBridge()

        # Crear pipeline de la cámara (Se procesa dentro del chip Movidius)
        self.pipeline = dai.Pipeline()

        # Nodos de las lentes
        self.camRgb = self.pipeline.create(dai.node.ColorCamera)
        self.monoLeft = self.pipeline.create(dai.node.MonoCamera)
        self.monoRight = self.pipeline.create(dai.node.MonoCamera)
        self.stereo = self.pipeline.create(dai.node.StereoDepth)

        # Nodos de salida USB
        self.xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        self.xoutDepth = self.pipeline.create(dai.node.XLinkOut)
        self.xoutRgb.setStreamName("rgb")
        self.xoutDepth.setStreamName("depth")

        # Configurar resoluciones
        self.camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
        self.camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        self.camRgb.setIspScale(1, 3) # Reduce resolución para el Wi-Fi (~640x360)

        self.monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        self.monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
        self.monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        self.monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

        # Configurar cálculo 3D
        self.stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        self.stereo.setLeftRightCheck(True)

        # Conectar los cables virtuales en la cámara
        self.camRgb.isp.link(self.xoutRgb.input)
        self.monoLeft.out.link(self.stereo.left)
        self.monoRight.out.link(self.stereo.right)
        self.stereo.disparity.link(self.xoutDepth.input)

        # Arrancar el dispositivo
        self.get_logger().info('Inyectando inteligencia artificial a la OAK-D Lite...')
        self.device = dai.Device(self.pipeline)
        
        # Colas de extracción USB
        self.qRgb = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        self.qDepth = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)

        # Timer de ROS 2
        self.timer = self.create_timer(0.033, self.timer_callback)
        self.get_logger().info('Tercer ojo activado. Publicando video RGB y Mapa de Profundidad.')

    def timer_callback(self):
        # Intentar obtener fotogramas
        inRgb = self.qRgb.tryGet()
        inDepth = self.qDepth.tryGet()

        if inRgb is not None:
            frame_rgb = inRgb.getCvFrame()
            msg_rgb = self.bridge.cv2_to_compressed_imgmsg(frame_rgb, dst_format='jpg')
            msg_rgb.header.frame_id = "oakd_link"
            self.pub_rgb.publish(msg_rgb)

        if inDepth is not None:
            # Obtener el mapa 3D y convertirlo a un mapa de color térmico visible
            frame_depth = inDepth.getFrame()
            disp_max = self.stereo.initialConfig.getMaxDisparity()
            frame_depth_vis = (frame_depth * (255.0 / disp_max)).astype(np.uint8)
            frame_depth_color = cv2.applyColorMap(frame_depth_vis, cv2.COLORMAP_JET)

            msg_depth = self.bridge.cv2_to_compressed_imgmsg(frame_depth_color, dst_format='jpg')
            msg_depth.header.frame_id = "oakd_link"
            self.pub_depth.publish(msg_depth)

def main(args=None):
    rclpy.init(args=args)
    node = MarvinOakDNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()