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
        self.BTN_REVERSE = 1        # Botón 1: Caja de Cambios (Mantener para Reversa)
        
        # --- PARÁMETROS FÍSICOS Y DE INERCIA ---
        self.MAX_LINEAR_SPEED = 0.7   # m/s
        self.UPDATE_RATE = 0.05       # 20 Hz (50 milisegundos)
        
        self.ACCEL_STEP = 0.6 * self.UPDATE_RATE   # Aceleración
        self.COAST_STEP = 0.2 * self.UPDATE_RATE   # Inercia libre (Freno regenerativo)
        self.BRAKE_STEP = 1.8 * self.UPDATE_RATE   # Freno de pedal
        
        # --- VARIABLES DE ESTADO INTERNO ---
        self.current_speed = 0.0
        self.target_steering = 0.0
        self.gas_pedal = 0.0
        self.brake_pedal = 0.0
        self.reverse_active = False

        # Reloj interno de físicas
        self.timer = self.create_timer(self.UPDATE_RATE, self.control_loop)
        
        self.get_logger().info("Nodo HORI: Modo Libre (Sin botón de seguridad) y Reversa activada.")

    def joy_callback(self, joy_msg):
        # Leemos si el botón de reversa está siendo presionado
        self.reverse_active = (joy_msg.buttons[self.BTN_REVERSE] == 1)
        
        raw_accel = joy_msg.axes[self.AXIS_ACCEL_PEDAL]
        raw_brake = joy_msg.axes[self.AXIS_BRAKE_PEDAL]
        
        self.gas_pedal = (1.0 - raw_accel) / 2.0 
        self.brake_pedal = (1.0 - raw_brake) / 2.0

        self.target_steering = joy_msg.axes[self.AXIS_STEERING]

    def control_loop(self):
        twist = Twist()
        
        # 1. LÓGICA DE FRENADO MANUAL (Pedal Izquierdo)
        if self.brake_pedal > 0.02:
            # Si vamos hacia adelante, restamos velocidad
            if self.current_speed > 0:
                self.current_speed -= self.BRAKE_STEP * self.brake_pedal
                if self.current_speed < 0: self.current_speed = 0.0 # Evitar que el freno cause reversa
            # Si vamos en reversa (velocidad negativa), sumamos para acercarnos a 0
            elif self.current_speed < 0:
                self.current_speed += self.BRAKE_STEP * self.brake_pedal
                if self.current_speed > 0: self.current_speed = 0.0
                
        # 2. LÓGICA DE ACELERACIÓN (Pedal Derecho)
        elif self.gas_pedal > 0.02:
            # Determinamos si queremos ir a +0.7 (Adelante) o -0.7 (Reversa)
            target_speed = self.gas_pedal * self.MAX_LINEAR_SPEED
            if self.reverse_active:
                target_speed = -target_speed
            
            # Suavizado de inercia hacia la velocidad objetivo
            if self.current_speed < target_speed:
                self.current_speed += self.ACCEL_STEP
            elif self.current_speed > target_speed:
                self.current_speed -= self.ACCEL_STEP
                
        # 3. LÓGICA DE INERCIA REGENERATIVA (Ningún pedal pisado)
        else:
            if self.current_speed > 0:
                self.current_speed -= self.COAST_STEP
                if self.current_speed < 0: self.current_speed = 0.0
            elif self.current_speed < 0:
                self.current_speed += self.COAST_STEP
                if self.current_speed > 0: self.current_speed = 0.0

        # --- LIMITES Y ASISTENTE DE ESTACIONAMIENTO ---
        
        # Si la velocidad absoluta (hacia adelante o atrás) es casi nula y no aceleramos, detenemos el auto.
        if abs(self.current_speed) < 0.05 and self.gas_pedal < 0.02:
            self.current_speed = 0.0
            
        # Bloquear velocidades por encima del máximo permitido físico
        if self.current_speed > self.MAX_LINEAR_SPEED:
            self.current_speed = self.MAX_LINEAR_SPEED
        elif self.current_speed < -self.MAX_LINEAR_SPEED:
            self.current_speed = -self.MAX_LINEAR_SPEED

        # --- EMPAQUETADO Y ENVÍO DEL MENSAJE ---
        twist.linear.x = self.current_speed
        twist.linear.y = self.target_steering * 0.045
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