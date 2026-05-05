from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='marvincar_camera',
            executable='camera_csi0',
            name='camera_csi0_node',
            output='screen',
        ),
        Node(
            package='marvincar_camera',
            executable='camera_csi1',
            name='camera_csi1_node',
            output='screen',
        ),
    ])
