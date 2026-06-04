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
        
        # --- CONFIGURACIÓN DE TU HORI APEX ---
        self.AXIS_STEERING = 0      # Volante
        self.AXIS_ACCEL_PEDAL = 5   # Pedal Derecho (Acelerador)
        self.AXIS_BRAKE_PEDAL = 2   # Pedal Izquierdo (Freno)
        self.BTN_DEADMAN = 1        # Botón de seguridad
        
        self.MAX_LINEAR_SPEED = 1.0  # m/s
        self.MAX_ANGULAR_SPEED = 1.5 # rad/s
        
        self.get_logger().info("Nodo del Volante HORI iniciado. Mantén presionado el botón 1 para moverte.")

    def joy_callback(self, joy_msg):
        twist = Twist()
        
        # Si el botón de seguridad (Botón 1) está presionado
        if joy_msg.buttons[self.BTN_DEADMAN] == 1:
            raw_accel = joy_msg.axes[self.AXIS_ACCEL_PEDAL]
            raw_brake = joy_msg.axes[self.AXIS_BRAKE_PEDAL]
            
            # ¡CORRECCIÓN DE LOS PEDALES!
            # Ahora, Reposo (1.0) -> 0.0 y Pisado a fondo (-1.0) -> 1.0
            accel_mapped = (1.0 - raw_accel) / 2.0 
            brake_mapped = (1.0 - raw_brake) / 2.0

            # Lógica de acelerador y freno
            if accel_mapped > 0.1:
                 twist.linear.x = accel_mapped * self.MAX_LINEAR_SPEED
            elif brake_mapped > 0.1:
                 twist.linear.x = -brake_mapped * self.MAX_LINEAR_SPEED
            else:
                 twist.linear.x = 0.0
                 
            # ¡CORRECCIÓN DE LA DIRECCIÓN!
            # Se eliminó el * -1.0 para que el giro coincida con el movimiento real
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