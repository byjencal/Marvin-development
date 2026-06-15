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
        
        # --- PARÁMETROS FÍSICOS Y DE INERCIA ---
        self.MAX_LINEAR_SPEED = 0.7   # m/s
        self.UPDATE_RATE = 0.05       # 20 Hz (50 milisegundos)
        
        # Tasas de cambio (m/s que se suman o restan en cada "tick" del reloj)
        # Puedes jugar con estos 3 valores para hacer el auto más pesado o más ligero
        self.ACCEL_STEP = 0.6 * self.UPDATE_RATE   # Qué tan rápido acelera
        self.COAST_STEP = 0.2 * self.UPDATE_RATE   # Freno regenerativo (Inercia natural)
        self.BRAKE_STEP = 1.8 * self.UPDATE_RATE   # Qué tan fuerte es el disco de freno izquierdo
        
        # --- VARIABLES DE ESTADO INTERNO ---
        self.current_speed = 0.0
        self.target_steering = 0.0
        self.gas_pedal = 0.0
        self.brake_pedal = 0.0
        self.deadman_active = False

        # Creamos el "Reloj Interno" que calculará la inercia independientemente de si tocas el volante o no
        self.timer = self.create_timer(self.UPDATE_RATE, self.control_loop)
        
        self.get_logger().info("Nodo HORI: Modo Auto Eléctrico (Inercia y Freno Real) activado.")

    def joy_callback(self, joy_msg):
        # 1. Guardamos el estado de los controles en las variables internas
        self.deadman_active = (joy_msg.buttons[self.BTN_DEADMAN] == 1)
        
        raw_accel = joy_msg.axes[self.AXIS_ACCEL_PEDAL]
        raw_brake = joy_msg.axes[self.AXIS_BRAKE_PEDAL]
        
        # Rango de 0.0 (suelto) a 1.0 (pisado a fondo)
        self.gas_pedal = (1.0 - raw_accel) / 2.0 
        self.brake_pedal = (1.0 - raw_brake) / 2.0

        self.target_steering = joy_msg.axes[self.AXIS_STEERING]

    # Esta función se ejecuta 20 veces por segundo automáticamente
    def control_loop(self):
        twist = Twist()
        
        if self.deadman_active:
            # 1. LÓGICA DE FRENADO MANUAL (Pedal Izquierdo)
            if self.brake_pedal > 0.02:
                # Restamos velocidad proporcional a qué tan fuerte pisas el freno
                self.current_speed -= self.BRAKE_STEP * self.brake_pedal
                
            # 2. LÓGICA DE ACELERACIÓN (Pedal Derecho)
            elif self.gas_pedal > 0.02:
                target_speed = self.gas_pedal * self.MAX_LINEAR_SPEED
                
                if self.current_speed < target_speed:
                    self.current_speed += self.ACCEL_STEP
                elif self.current_speed > target_speed:
                    self.current_speed -= self.COAST_STEP # Si aflojas el pie, baja suavemente
                    
            # 3. LÓGICA DE INERCIA REGENERATIVA (Ningún pedal pisado)
            else:
                self.current_speed -= self.COAST_STEP
                
        else:
            # Si sueltas el botón de seguridad 1, el auto se detiene un poco más rápido por seguridad
            self.current_speed -= self.COAST_STEP * 2.0

        # --- LIMITES Y ASISTENTE DE ESTACIONAMIENTO ---
        
        # Asistente: Si el auto va muy lento rodando solo, lo paramos por completo.
        if self.current_speed < 0.05 and self.gas_pedal < 0.02:
            self.current_speed = 0.0
            
        # Límite Físico: El auto nunca puede ir en reversa (< 0.0) ni rebasar el máximo
        if self.current_speed < 0.0:
            self.current_speed = 0.0
        elif self.current_speed > self.MAX_LINEAR_SPEED:
            self.current_speed = self.MAX_LINEAR_SPEED

        # --- EMPAQUETADO Y ENVÍO DEL MENSAJE ---
        twist.linear.x = self.current_speed
        
        # Dirección directa al servo (Hack de Yahboom)
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