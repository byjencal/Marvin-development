#!/usr/bin/env python3
"""
Lanza todos los nodos del sistema MARVIN en una sola terminal:
1. Driver Ackman (bringup)
2. LIDAR LD19
3. SLAM Toolbox (mapping)

Uso: ros2 launch marvincar_bringup full_system_launch.py
"""

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # Directorio de paquetes
    marvincar_bringup_dir = get_package_share_directory('marvincar_bringup')
    marvin_lidar_dir = get_package_share_directory('marvin_lidar')
    marvincar_nav_dir = get_package_share_directory('marvincar_nav')

    # 1. Launch Bringup (Driver Ackman)
    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(marvincar_bringup_dir, 'launch', 'marvincar_bringup_launch.py')
        )
    )

    # 2. Launch LIDAR LD19
    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(marvin_lidar_dir, 'launch', 'ld19.launch.py')
        )
    )

    # 3. Launch SLAM Mapping
    mapping_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(marvincar_nav_dir, 'launch', 'mapping_launch.py')
        )
    )

    return LaunchDescription([
        bringup_launch,
        lidar_launch,
        mapping_launch,
    ])
