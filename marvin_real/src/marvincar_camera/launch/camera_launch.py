#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """
    Launch file for camera nodes
    Starts both CSI camera streams (camera_0 and camera_1)
    """

    package_path = get_package_share_directory('marvincar_camera')
    param_file = os.path.join(package_path, 'param', 'camera_params.yaml')

    camera_node = Node(
        package='marvincar_camera',
        executable='camera_node',
        name='camera_node',
        output='screen',
        parameters=[param_file],
    )

    return LaunchDescription([
        camera_node,
    ])
