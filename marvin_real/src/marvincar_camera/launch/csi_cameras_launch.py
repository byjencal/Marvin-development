from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    """
    Launch file para iniciar dos nodos de cámara CSI (sensor_id 0 y 1).
    Las imágenes se publican en:
      - /camera_0/image_raw
      - /camera_1/image_raw
    
    Visible en RViz agregando dos complementos Image con estos tópicos.
    """
    
    # Ruta absoluta al script
    script_path = '/root/marvin/marvin_real/src/marvincar_camera/marvincar_camera/csi_camera_node.py'
    
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
    camera_0_node = ExecuteProcess(
        cmd=['python3', '-u', script_path, '--ros-args', '-p', 'sensor_id:=0'],
        name='camera_0_node',
        output='screen',
        emulate_tty=True,
        shell=False,
    )

    # Nodo para la cámara 1 (sensor-id=1)
    camera_1_node = ExecuteProcess(
        cmd=['python3', '-u', script_path, '--ros-args', '-p', 'sensor_id:=1'],
        name='camera_1_node',
        output='screen',
        emulate_tty=True,
        shell=False,
    )

    return LaunchDescription([
        capture_width_arg,
        capture_height_arg,
        framerate_arg,
        camera_0_node,
        camera_1_node,
    ])
