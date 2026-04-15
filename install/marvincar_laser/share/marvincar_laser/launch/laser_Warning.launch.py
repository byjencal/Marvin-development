from launch import LaunchDescription
from launch_ros.actions import Node

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    laser_Avoidance_node = Node(
        package='marvincar_laser',
        executable='laser_Warning',
    )
  

    
    launch_description = LaunchDescription([laser_Avoidance_node]) 
    return launch_description
