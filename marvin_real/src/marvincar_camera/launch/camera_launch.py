#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """
    Launch file for camera nodes
    Starts both USB camera streams (camera_0 and camera_1)
    """

    camera_node = Node(
        package='marvincar_camera',
        executable='camera_node',
        name='camera_node',
        output='screen',
        parameters=[
            {'camera_0_device': '/dev/video0'},
            {'camera_1_device': '/dev/video1'},
            {'fps': 30},
            {'camera_0_frame_id': 'camera_0'},
            {'camera_1_frame_id': 'camera_1'},
        ]
    )

    return LaunchDescription([
        camera_node,
    ])
