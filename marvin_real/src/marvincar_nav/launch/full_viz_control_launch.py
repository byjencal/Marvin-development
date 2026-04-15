#!/usr/bin/env python3
"""
Lanza la visualización del mapa en RViz en la laptop.

Uso: ros2 launch marvincar_nav full_viz_control_launch.py

Nota: el teleop (control por teclado) se lanza en otra terminal con:
    ros2 run teleop_twist_keyboard teleop_twist_keyboard
"""

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # Directorio del paquete
    marvincar_nav_dir = get_package_share_directory('marvincar_nav')

    # Launch RViz para visualizar el mapa
    view_map_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(marvincar_nav_dir, 'launch', 'view_map_launch.py')
        )
    )

    return LaunchDescription([
        view_map_launch,
    ])
