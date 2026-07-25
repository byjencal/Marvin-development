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
        
        self.AXIS_STEERING = 0      
        self.AXIS_ACCEL_PEDAL = 5   
        self.AXIS_BRAKE_PEDAL = 2   
        self.BTN_REVERSE = 1        
        
        self.MAX_LINEAR_SPEED = 3  # m/s, valor alto para prueba de velocidad maxima del motor
        self.get_logger().info("Nodo HORI: Modo Telemetría Puro. Físicas transferidas a M.A.R.V.I.N.")

    def joy_callback(self, joy_msg):
        twist = Twist()
        
        reverse_active = (joy_msg.buttons[self.BTN_REVERSE] == 1)
        raw_accel = joy_msg.axes[self.AXIS_ACCEL_PEDAL]
        raw_brake = joy_msg.axes[self.AXIS_BRAKE_PEDAL]
        
        gas_pedal = (1.0 - raw_accel) / 2.0 
        brake_pedal = (1.0 - raw_brake) / 2.0

        # 1. Velocidad Objetivo
        target_speed = 0.0
        if gas_pedal > 0.02:
            target_speed = gas_pedal * self.MAX_LINEAR_SPEED
            if reverse_active:
                target_speed = -target_speed
                
        # 2. Intensidad de Freno de Disco (Enviado por el canal Z)
        brake_intensity = 0.0
        if brake_pedal > 0.02:
            brake_intensity = brake_pedal

        # 3. Dirección
        target_steering = joy_msg.axes[self.AXIS_STEERING] * 0.045

        # Empaquetamos todo
        twist.linear.x = target_speed
        twist.linear.y = target_steering
        twist.linear.z = brake_intensity 
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
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
