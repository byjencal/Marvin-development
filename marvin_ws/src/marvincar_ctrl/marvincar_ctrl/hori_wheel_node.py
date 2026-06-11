#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

class HoriWheelNode(Node):
    def __init__(self):
        super().__init__('hori_wheel_node')
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.joy_sub = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        
        # --- CONFIGURACIÓN DE TU HORI APEX ---
        self.AXIS_STEERING = 0      # Volante
        self.AXIS_ACCEL_PEDAL = 5   # Pedal Derecho (Acelerador)
        self.AXIS_BRAKE_PEDAL = 2   # Pedal Izquierdo (Freno)
        self.BTN_DEADMAN = 1        # Botón de seguridad
        
        # VELOCIDADES ÓPTIMAS REALES (Ajustadas al hardware físico de Yahboom)
        self.MAX_LINEAR_SPEED = 0.7  # m/s (Velocidad física máxima real del chasis)
        self.MAX_ANGULAR_SPEED = 1.0 # rad/s (Alineado con los grados máximos del servo)
        
        self.get_logger().info("Nodo HORI (Conducción Proporcional Avanzada) iniciado.")

    def joy_callback(self, joy_msg):
        twist = Twist()
        
        # 1. ACELERACIÓN Y VELOCIDAD FANTASMA
        if joy_msg.buttons[self.BTN_DEADMAN] == 1:
            raw_accel = joy_msg.axes[self.AXIS_ACCEL_PEDAL]
            raw_brake = joy_msg.axes[self.AXIS_BRAKE_PEDAL]
            
            accel_mapped = (1.0 - raw_accel) / 2.0 
            brake_mapped = (1.0 - raw_brake) / 2.0

            if accel_mapped > 0.02:
                 twist.linear.x = accel_mapped * self.MAX_LINEAR_SPEED
            elif brake_mapped > 0.02:
                 twist.linear.x = -brake_mapped * self.MAX_LINEAR_SPEED
            else:
                 # HACK 1: Velocidad Fantasma (0.01 m/s)
                 # Es tan débil que los motores físicos no tendrán fuerza para mover el peso del carro,
                 # pero engaña a la placa Yahboom para que mantenga activo el servo de dirección.
                 twist.linear.x = 0.01
        else:
            twist.linear.x = 0.01

        # 2. EL TRUCO DE CANCELACIÓN DE ACKERMANN
        raw_steering = joy_msg.axes[self.AXIS_STEERING]
        
        # Factor para mantener la escala de giro original
        steering_factor = self.MAX_ANGULAR_SPEED / self.MAX_LINEAR_SPEED
        
        # HACK 2: Al multiplicar el volante por la velocidad (twist.linear.x), 
        # cuando la Jetson lo divida internamente, el resultado será el ángulo puro.
        twist.angular.z = raw_steering * twist.linear.x * steering_factor

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