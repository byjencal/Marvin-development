from launch import LaunchDescription
from launch_ros.actions import Node

#name file: hori_teleop.launch.py
#Ruta marvin_ws/src/marvincar_ctrl/launch/hori_teleop.launch.py
def generate_launch_description():
    return LaunchDescription([
        # 1. Nodo oficial que lee el USB del volante
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen',
            parameters=[{
                'deadzone': 0.05,
                'autorepeat_rate': 20.0,
            }]
        ),
        # 2. Tu nodo personalizado que traduce los pedales a cmd_vel
        Node(
            package='marvincar_ctrl',
            executable='hori_wheel_node',
            name='hori_wheel_node',
            output='screen'
        )
    ])