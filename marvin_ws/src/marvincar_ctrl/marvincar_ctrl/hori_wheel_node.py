#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

class HoriWheelNode(Node):
    def __init__(self):
        super().__init__('hori_wheel_node')
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.joy_sub = self.create_subscription(Joy, 'joy', self.joy_callback, 10)
        
        # --- MAPEADO DE EJES DEL HORI APEX ---
        # Ejecuta 'jstest /dev/input/js0' para confirmar estos números
        self.AXIS_STEERING = 0      # Volante
        self.AXIS_ACCEL_PEDAL = 1   # Acelerador
        self.AXIS_BRAKE_PEDAL = 2   # Freno
        self.BTN_DEADMAN = 5        # Botón de seguridad (Ej: R2 o L2)
        
        self.MAX_LINEAR_SPEED = 1.0  # m/s
        self.MAX_ANGULAR_SPEED = 1.5 # rad/s
        
        self.get_logger().info("Nodo del Volante HORI iniciado. Mantén presionado el botón de seguridad para moverte.")

    def joy_callback(self, joy_msg):
        twist = Twist()
        
        if joy_msg.buttons[self.BTN_DEADMAN] == 1:
            raw_accel = joy_msg.axes[self.AXIS_ACCEL_PEDAL]
            raw_brake = joy_msg.axes[self.AXIS_BRAKE_PEDAL]
            
            # Lógica de acelerador y freno
            if raw_accel > 0.1:
                 twist.linear.x = raw_accel * self.MAX_LINEAR_SPEED
            elif raw_brake > 0.1:
                 twist.linear.x = -raw_brake * self.MAX_LINEAR_SPEED
            else:
                 twist.linear.x = 0.0
                 
            # Lógica de dirección
            raw_steering = joy_msg.axes[self.AXIS_STEERING]
            twist.angular.z = raw_steering * self.MAX_ANGULAR_SPEED
        else:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.cmd_vel_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = HoriWheelNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_vel_pub.publish(Twist()) # Freno de emergencia al cerrar
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()