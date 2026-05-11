from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    """
    Launch file para iniciar dos nodos de cámara CSI (sensor_id 0 y 1).
    Las imágenes se publican en:
      - /camera_0/image_raw
      - /camera_1/image_raw
    
    Visible en RViz agregando dos complementos Image con estos tópicos.
    """
    
    # Argumentos declarativos para configuración
    capture_width_arg = DeclareLaunchArgument(
        'capture_width',
        default_value='1920',
        description='Capture width in pixels'
    )
    
    capture_height_arg = DeclareLaunchArgument(
        'capture_height',
        default_value='1080',
        description='Capture height in pixels'
    )
    
    framerate_arg = DeclareLaunchArgument(
        'framerate',
        default_value='20',
        description='Framerate in Hz'
    )

    # Nodo para la cámara 0 (sensor-id=0)
    camera_0_node = Node(
        package='marvincar_camera',
        executable='csi_camera_node',
        name='camera_0_node',
        parameters=[
            {
                'sensor_id': 0,
                'sensor_mode': 0,
                'capture_width': LaunchConfiguration('capture_width'),
                'capture_height': LaunchConfiguration('capture_height'),
                'framerate': LaunchConfiguration('framerate'),
            }
        ],
        output='screen',
        emulate_tty=True,
        prefix=['python3 -u'],
    )

    # Nodo para la cámara 1 (sensor-id=1)
    camera_1_node = Node(
        package='marvincar_camera',
        executable='csi_camera_node',
        name='camera_1_node',
        parameters=[
            {
                'sensor_id': 1,
                'sensor_mode': 0,
                'capture_width': LaunchConfiguration('capture_width'),
                'capture_height': LaunchConfiguration('capture_height'),
                'framerate': LaunchConfiguration('framerate'),
            }
        ],
        output='screen',
        emulate_tty=True,
        prefix=['python3 -u'],
    )

    return LaunchDescription([
        capture_width_arg,
        capture_height_arg,
        framerate_arg,
        camera_0_node,
        camera_1_node,
    ])
