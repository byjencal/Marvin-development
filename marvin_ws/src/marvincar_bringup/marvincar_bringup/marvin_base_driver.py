#!/usr/bin/env python3
# encoding: utf-8

import random
from Rosmaster_Lib import Rosmaster

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Int32, Bool
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu, MagneticField, JointState

class MarvinBaseDriver(Node):
    def __init__(self, name):
        super().__init__(name)
        self.car = Rosmaster('/dev/ttyUSB0')
        self.car.set_car_type(5)
        
        self.declare_parameter('imu_link', 'imu_link')
        self.imu_link = self.get_parameter('imu_link').get_parameter_value().string_value
        self.declare_parameter('Prefix', "")
        self.Prefix = self.get_parameter('Prefix').get_parameter_value().string_value

        self.sub_cmd_vel = self.create_subscription(Twist,"cmd_vel",self.cmd_vel_callback,1)
        self.sub_RGBLight = self.create_subscription(Int32,"RGBLight",self.RGBLightcallback,100)
        self.sub_BUzzer = self.create_subscription(Bool,"Buzzer",self.Buzzercallback,100)

        self.EdiPublisher = self.create_publisher(Float32,"edition",100)
        self.volPublisher = self.create_publisher(Float32,"voltage",100)
        self.staPublisher = self.create_publisher(JointState,"joint_states",100)
        self.velPublisher = self.create_publisher(Twist,"vel_raw",50)
        self.imuPublisher = self.create_publisher(Imu,"/imu/data_raw",100)
        self.magPublisher = self.create_publisher(MagneticField,"/imu/mag",100)
        
        self.timer = self.create_timer(0.1, self.pub_data)
        self.encoder_timer = self.create_timer(1.0, self.show_encoder_data)

        # --- MOTOR FÍSICO E INERCIA INCORPORADA EN LA JETSON ---
        self.MAX_LINEAR_SPEED = 2.0  # m/s  
        self.UPDATE_RATE = 0.05       # 20 Hz
        
        self.ACCELERATION = 2.0          # m/s^2
        self.COAST_DECELERATION = 0.5    # m/s^2
        self.BRAKE_DECELERATION = 5.0    # m/s^2

        self.ACCEL_STEP = self.ACCELERATION * self.UPDATE_RATE
        self.COAST_STEP = self.COAST_DECELERATION * self.UPDATE_RATE
        self.BRAKE_STEP = self.BRAKE_DECELERATION * self.UPDATE_RATE
        
        self.current_vx = 0.0
        self.target_vx = 0.0
        self.target_vy = 0.0
        self.brake_intensity = 0.0
        
        self.last_cmd_time = self.get_clock().now()
        
        # Reloj de inercia
        self.physics_timer = self.create_timer(self.UPDATE_RATE, self.physics_loop)
        # -------------------------------------------------------

        self.edition = Float32()
        self.edition.data = 1.0
        self.car.create_receive_threading()
        self.car.set_beep(200)
        self.get_logger().info("Buzzer test: beep de arranque de 200 ms")

    def cmd_vel_callback(self,msg):
        if not isinstance(msg, Twist): return
        
        # Recibimos la intención del piloto desde el Wi-Fi
        self.target_vx = msg.linear.x
        self.target_vy = msg.linear.y
        self.brake_intensity = msg.linear.z # Pedal izquierdo mapeado aquí
        
        # Reseteamos el temporizador de emergencia
        self.last_cmd_time = self.get_clock().now()

    def physics_loop(self):
        now = self.get_clock().now()
        time_since_last_cmd = (now - self.last_cmd_time).nanoseconds / 1e9
        
        # --- WATCHDOG: FRENO DE EMERGENCIA POR CORTE DE WI-FI ---
        if time_since_last_cmd > 0.5:
            self.target_vx = 0.0
            self.brake_intensity = 0.8  # Pisa el freno al 80% automáticamente si se corta el internet
            
        # 1. Freno Manual o de Emergencia
        if self.brake_intensity > 0.02:
            if self.current_vx > 0:
                self.current_vx -= self.BRAKE_STEP * self.brake_intensity
                if self.current_vx < 0: self.current_vx = 0.0
            elif self.current_vx < 0:
                self.current_vx += self.BRAKE_STEP * self.brake_intensity
                if self.current_vx > 0: self.current_vx = 0.0
                
        # 2. Aceleración
        elif abs(self.target_vx) > 0.02:
            if self.current_vx < self.target_vx:
                self.current_vx += self.ACCEL_STEP
                if self.current_vx > self.target_vx: self.current_vx = self.target_vx
            elif self.current_vx > self.target_vx:
                self.current_vx -= self.ACCEL_STEP
                if self.current_vx < self.target_vx: self.current_vx = self.target_vx
                
        # 3. Inercia Regenerativa
        else:
            if self.current_vx > 0:
                self.current_vx -= self.COAST_STEP
                if self.current_vx < 0: self.current_vx = 0.0
            elif self.current_vx < 0:
                self.current_vx += self.COAST_STEP
                if self.current_vx > 0: self.current_vx = 0.0
                
        # Asistente de Estacionamiento
        if abs(self.current_vx) < 0.05 and abs(self.target_vx) < 0.02 and self.brake_intensity < 0.02:
            self.current_vx = 0.0

        # Límites de hardware
        if self.current_vx > self.MAX_LINEAR_SPEED: self.current_vx = self.MAX_LINEAR_SPEED
        elif self.current_vx < -self.MAX_LINEAR_SPEED: self.current_vx = -self.MAX_LINEAR_SPEED

        # Enviar comandos de velocidad física y ángulo absoluto al microcontrolador
        self.car.set_car_motion(self.current_vx, self.target_vy, 0.0)

    def RGBLightcallback(self,msg):
        if not isinstance(msg, Int32): return
        for i in range(3): self.car.set_colorful_effect(msg.data, 6, parm=1)
        
    def Buzzercallback(self,msg):
        if not isinstance(msg, Bool): return
        beep_time = 1 if msg.data else 0
        for i in range(3): self.car.set_beep(beep_time)

    def show_encoder_data(self):
        m1, m2, m3, m4 = self.car.get_motor_encoder()
        self.get_logger().info(
            "encoder m1: %d, m2: %d, m3: %d, m4: %d" % (m1, m2, m3, m4)
        )

    def pub_data(self):
        time_stamp = self.get_clock().now()
        imu = Imu()
        twist = Twist()
        battery = Float32()
        edition = Float32()
        mag = MagneticField()
        state = JointState()
        state.header.stamp = time_stamp.to_msg()
        state.header.frame_id = "joint_states"
        if len(self.Prefix)==0:
            state.name = ["joint_back_wheel_right", "joint_back_wheel_left","joint_front_handle_left","joint_front_wheel_left",
                            "joint_front_handle_right", "joint_front_wheel_right"]
        else:
            state.name = [self.Prefix+"joint_back_wheel_right",self.Prefix+ "joint_back_wheel_left",self.Prefix+"joint_front_handle_left",self.Prefix+"joint_front_wheel_left",
                            self.Prefix+"joint_front_handle_right", self.Prefix+"joint_front_wheel_right"]
        
        edition.data = self.car.get_version()*1.0
        battery.data = self.car.get_battery_voltage()*1.0
        ax, ay, az = self.car.get_accelerometer_data()
        gx, gy, gz = self.car.get_gyroscope_data()
        mx, my, mz = self.car.get_magnetometer_data()
        mx = mx * 1.0
        my = my * 1.0
        mz = mz * 1.0
        vx, vy, angular = self.car.get_motion_data()
        
        imu.header.stamp = time_stamp.to_msg()
        imu.header.frame_id = self.imu_link
        imu.linear_acceleration.x = ax*1.0
        imu.linear_acceleration.y = ay*1.0
        imu.linear_acceleration.z = az*1.0
        imu.angular_velocity.x = gx*1.0
        imu.angular_velocity.y = gy*1.0
        imu.angular_velocity.z = gz*1.0

        mag.header.stamp = time_stamp.to_msg()
        mag.header.frame_id = self.imu_link
        mag.magnetic_field.x = mx*1.0
        mag.magnetic_field.y = my*1.0
        mag.magnetic_field.z = mz*1.0
        
        twist.linear.x = vx*1.0    
        twist.linear.y = vy*1000*1.0   
        # twist.angular.z = angular*1.0    
        # self.velPublisher.publish(twist)
        
        # self.imuPublisher.publish(imu)
        # self.magPublisher.publish(mag)
        # self.volPublisher.publish(battery)
        # self.EdiPublisher.publish(edition)
        
        steer_radis = vy*1000.0*3.1416/180.0
        state.position = [0.0, 0.0, steer_radis, 0.0, steer_radis, 0.0]
        if not vx == angular == 0:
            i = random.uniform(-3.14, 3.14)
            state.position = [i, i, steer_radis, i, steer_radis, i]
        # self.staPublisher.publish(state)
            
def main():
    rclpy.init() 
    driver = MarvinBaseDriver('marvin_base_driver')
    rclpy.spin(driver)

if __name__ == '__main__':
    main()
