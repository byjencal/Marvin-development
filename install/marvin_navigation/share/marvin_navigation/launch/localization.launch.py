import os
from ament_index_python.packages import get_package_share_directory,get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Get the launch directory
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_pkg_path = get_package_share_path('marvin_navigation')
    map_path = map_pkg_path / 'maps/marvin_world.yaml'

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation (Gazebo) clock if true')

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(
                'nav2_bringup'), 'launch', 'localization_launch.py'
        )]), launch_arguments={'use_sim_time': use_sim_time,
                               'map': str(map_path)}.items()
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        localization
    ])
