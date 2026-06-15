from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='marvincar_vision',
            executable='stereo_camera_node',
            name='marvin_stereo_camera',
            output='screen'
        ),
        Node(
            package='marvincar_vision',
            executable='oakd_node',
            name='marvin_oakd_node',
            output='screen'
        )
    ])
