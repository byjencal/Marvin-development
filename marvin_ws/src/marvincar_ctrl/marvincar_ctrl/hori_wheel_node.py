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
        
        # 1. DIRECCIÓN INDEPENDIENTE
        # El servo lee la posición de tu volante sin importar si aceleras, frenas o presionas botones.
        # Si tienes el volante girado y no lo sueltas, las ruedas se quedarán giradas.
        raw_steering = joy_msg.axes[self.AXIS_STEERING]
        twist.angular.z = raw_steering * self.MAX_ANGULAR_SPEED
        
        # 2. ACELERACIÓN PROPORCIONAL
        # Solo aplicamos velocidad si el botón de seguridad está presionado
        if joy_msg.buttons[self.BTN_DEADMAN] == 1:
            raw_accel = joy_msg.axes[self.AXIS_ACCEL_PEDAL]
            raw_brake = joy_msg.axes[self.AXIS_BRAKE_PEDAL]
            
            accel_mapped = (1.0 - raw_accel) / 2.0 
            brake_mapped = (1.0 - raw_brake) / 2.0

            # Reducimos la 'zona muerta' a 0.02 para que sea sensible desde el primer milímetro
            if accel_mapped > 0.02:
                 twist.linear.x = accel_mapped * self.MAX_LINEAR_SPEED
            elif brake_mapped > 0.02:
                 twist.linear.x = -brake_mapped * self.MAX_LINEAR_SPEED
            else:
                 twist.linear.x = 0.0
        else:
            # Si sueltas el botón, el robot deja de avanzar, pero NO reseteamos angular.z
            twist.linear.x = 0.0

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