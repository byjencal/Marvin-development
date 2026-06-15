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
        
        # VELOCIDAD LINEAL
        self.MAX_LINEAR_SPEED = 0.7  # m/s
        
        self.get_logger().info("Nodo HORI: Modo de Control Directo del Servo Activado.")

    def joy_callback(self, joy_msg):
        twist = Twist()
        
        # 1. ACELERACIÓN
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
                 twist.linear.x = 0.0
        else:
            twist.linear.x = 0.0

        # 2. CONTROL DIRECTO DE DIRECCIÓN (Hack de Yahboom R2)
        raw_steering = joy_msg.axes[self.AXIS_STEERING]
        
        # Multiplicamos el giro bruto [-1.0 a 1.0] por 0.045 (que son 45 grados en la lógica de Yahboom).
        # Nota: Si las ruedas giran al revés, simplemente cambia 0.045 por -0.045
        twist.linear.y = raw_steering * 0.045
        
        # Silenciamos el angular.z para que el firmware de Yahboom no intente sobreescribir nuestro ángulo
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