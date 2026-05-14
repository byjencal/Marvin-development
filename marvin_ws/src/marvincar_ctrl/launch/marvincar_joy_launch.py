from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    joy_node = Node(
        package= 'joy',
        executable='joy_node',
	)
    marvincar_joy_node = Node(
        package= 'marvincar_ctrl',
        executable='marvincar_joy_marvin',
	)
    return LaunchDescription([
        joy_node,
        marvincar_joy_node
	])