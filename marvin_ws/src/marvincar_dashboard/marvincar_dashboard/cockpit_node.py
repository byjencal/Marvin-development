#!/usr/bin/env python3

import sys

import cv2
import numpy as np
import rclpy
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QMainWindow, QWidget
from rclpy.context import Context
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.utilities import remove_ros_args
from sensor_msgs.msg import CompressedImage


LEFT_TOPIC = 'camera_left/image_raw/compressed'
CENTER_TOPIC = 'oakd/color/image_raw/compressed'
RIGHT_TOPIC = 'camera_right/image_raw/compressed'


class DashboardRosNode(Node):
    def __init__(self, left_callback, center_callback, right_callback, context):
        super().__init__('marvincar_cockpit_dashboard', context=context)

        self._left_callback = left_callback
        self._center_callback = center_callback
        self._right_callback = right_callback

        self.create_subscription(
            CompressedImage,
            LEFT_TOPIC,
            self._on_left_image,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            CompressedImage,
            CENTER_TOPIC,
            self._on_center_image,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            CompressedImage,
            RIGHT_TOPIC,
            self._on_right_image,
            qos_profile_sensor_data,
        )

        self.get_logger().info('M.A.R.V.I.N. cockpit dashboard subscribed to compressed video streams.')

    def _on_left_image(self, msg):
        self._decode_and_emit(msg, self._left_callback, 'left')

    def _on_center_image(self, msg):
        self._decode_and_emit(msg, self._center_callback, 'center')

    def _on_right_image(self, msg):
        self._decode_and_emit(msg, self._right_callback, 'right')

    def _decode_and_emit(self, msg, frame_callback, camera_name):
        encoded_image = np.frombuffer(msg.data, dtype=np.uint8)
        frame = cv2.imdecode(encoded_image, cv2.IMREAD_COLOR)

        if frame is None:
            self.get_logger().warning(
                f'Could not decode compressed frame from {camera_name} camera.',
                throttle_duration_sec=5.0,
            )
            return

        frame_callback(frame)


class RosVideoThread(QThread):
    left_frame = pyqtSignal(np.ndarray)
    center_frame = pyqtSignal(np.ndarray)
    right_frame = pyqtSignal(np.ndarray)

    def __init__(self, ros_args=None, parent=None):
        super().__init__(parent)
        self._ros_args = ros_args
        self._context = None
        self._node = None

    def run(self):
        self._context = Context()

        try:
            rclpy.init(args=self._ros_args, context=self._context)
            self._node = DashboardRosNode(
                self.left_frame.emit,
                self.center_frame.emit,
                self.right_frame.emit,
                context=self._context,
            )
            rclpy.spin(self._node)
        except (ExternalShutdownException, KeyboardInterrupt):
            pass
        finally:
            if self._node is not None:
                self._node.destroy_node()
                self._node = None

            if self._context is not None:
                rclpy.try_shutdown(context=self._context)
                self._context = None

    def stop(self):
        self.requestInterruption()

        if self._context is not None:
            rclpy.try_shutdown(context=self._context)


class CockpitWindow(QMainWindow):
    def __init__(self, ros_args=None):
        super().__init__()
        self.setWindowTitle('M.A.R.V.I.N. Cockpit')

        central_widget = QWidget()
        central_widget.setObjectName('cockpitRoot')
        self.setCentralWidget(central_widget)

        layout = QGridLayout(central_widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setHorizontalSpacing(18)
        layout.setVerticalSpacing(18)

        self.left_label = self._create_video_label('Espejo Izquierdo', 400, 300)
        self.center_label = self._create_video_label('Parabrisas', 800, 450)
        self.right_label = self._create_video_label('Espejo Derecho', 400, 300)

        layout.addWidget(self.left_label, 0, 0, alignment=Qt.AlignCenter)
        layout.addWidget(self.center_label, 0, 1, alignment=Qt.AlignCenter)
        layout.addWidget(self.right_label, 0, 2, alignment=Qt.AlignCenter)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #05070a;
            }
            QWidget#cockpitRoot {
                background-color: #05070a;
            }
            QLabel#videoSurface {
                background-color: #10161d;
                border: 2px solid #2f4357;
                border-radius: 8px;
                color: #d8e7f5;
                font-size: 22px;
                font-weight: 700;
            }
        """)

        self.ros_thread = RosVideoThread(ros_args=ros_args, parent=self)
        self.ros_thread.left_frame.connect(self._update_left_frame)
        self.ros_thread.center_frame.connect(self._update_center_frame)
        self.ros_thread.right_frame.connect(self._update_right_frame)
        self.ros_thread.start()

    def _create_video_label(self, title, width, height):
        label = QLabel(title)
        label.setObjectName('videoSurface')
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(width, height)
        label.setScaledContents(False)
        return label

    def _update_left_frame(self, frame):
        self._set_frame(self.left_label, frame)

    def _update_center_frame(self, frame):
        self._set_frame(self.center_label, frame)

    def _update_right_frame(self, frame):
        self._set_frame(self.right_label, frame)

    def _set_frame(self, label, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_frame.shape
        bytes_per_line = channels * width

        image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888,
        ).copy()

        pixmap = QPixmap.fromImage(image).scaled(
            label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.ros_thread.stop()
        self.ros_thread.wait(3000)
        super().closeEvent(event)


def main(args=None):
    ros_args = sys.argv if args is None else args
    qt_args = remove_ros_args(args=ros_args)
    app = QApplication(qt_args)

    window = CockpitWindow(ros_args=ros_args)
    app.aboutToQuit.connect(window.ros_thread.stop)
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
