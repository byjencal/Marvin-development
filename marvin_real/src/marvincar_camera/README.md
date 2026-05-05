# marvincar_camera

Nodos ROS2 para publicar imágenes capturadas de ambas cámaras CSI (IMX219).

## Descripción

Este paquete contiene dos nodos independientes que capturan video de las cámaras IMX219 conectadas a los puertos CSI0 y CSI1 de la Jetson:

- `camera_csi0_node`: Publica imágenes de CSI0 en `/marvin/camera/csi0/image_raw`
- `camera_csi1_node`: Publica imágenes de CSI1 en `/marvin/camera/csi1/image_raw`

Ambos nodos usan:
- GStreamer con `nvarguscamerasrc` para hardware acceleration de Jetson
- OpenCV como interfaz para captura
- `cv_bridge` para convertir imágenes a formato ROS2 (sensor_msgs/Image)

## Requisitos

- ROS2 (instalado en Jetson)
- OpenCV con soporte GStreamer
- CUDA/cuDNN (típicamente pre-instalado en Jetson)
- cv_bridge
- Cámaras IMX219 conectadas a CSI0 y CSI1

## Compilación

```bash
# En el workspace MARVIN
cd ~/MARVIN/marvin_real
colcon build --packages-select marvincar_camera
```

## Uso

### Lanzar ambas cámaras

```bash
source ~/MARVIN/marvin_real/install/setup.bash
export ROS_DOMAIN_ID=1
ros2 launch marvincar_camera camera.launch.py
```

### Lanzar solo una cámara

```bash
# CSI0
ros2 run marvincar_camera camera_csi0

# CSI1
ros2 run marvincar_camera camera_csi1
```

## Visualización

### Con RViz

```bash
# En otra terminal
ros2 rviz2
# Agregar un Image display
# Topic: /marvin/camera/csi0/image_raw o /marvin/camera/csi1/image_raw
```

### Con `image_view`

```bash
# CSI0
ros2 run image_common image_view image:=/marvin/camera/csi0/image_raw

# CSI1
ros2 run image_common image_view image:=/marvin/camera/csi1/image_raw
```

## Tópicos publicados

- `/marvin/camera/csi0/image_raw` - Imágenes de CSI0 (sensor_msgs/Image)
- `/marvin/camera/csi1/image_raw` - Imágenes de CSI1 (sensor_msgs/Image)

## Parámetros

Actualmente sin parámetros configurables. Para cambiar resolución, framerate o propiedades del pipeline, editar:
- `camera_csi0_node.py` línea con `self.gst_pipeline`
- `camera_csi1_node.py` línea con `self.gst_pipeline`

Ejemplo para cambiar a 30 FPS y 1280x720:
```python
self.gst_pipeline = (
    'nvarguscamerasrc sensor-id=0 ! '
    'video/x-raw(memory:NVMM),width=1280,height=720,framerate=30/1 ! '
    ...
)
```

## Troubleshooting

### "Failed to open CSI camera"
- Verificar que las cámaras estén conectadas
- Probar primero con `nvgstcapture-1.0` para verificar funcionamiento

### No hay imágenes publicadas
- Verificar que ROS2 esté corriendo: `ros2 topic list`
- Ver logs: `ros2 topic echo /marvin/camera/csi0/image_raw`
- Aumentar output en launch file si está con `output='screen'`
