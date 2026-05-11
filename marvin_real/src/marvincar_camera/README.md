# marvincar_camera

Paquete ROS2 para controlar dos cámaras CSI IMX219 en Jetson Nano.

## Descripción

Este paquete proporciona un nodo parametrizable para capturar imágenes de cámaras CSI y publicarlas como mensajes ROS2 `sensor_msgs/Image`. Está optimizado para Jetson Nano usando la canalización de GStreamer con `nvarguscamerasrc`.

## Hardware

- **Jetson Nano Developer Kit**
- **Dos cámaras IMX219 CSI** (conectadas a los puertos CSI)
- **Ubuntu 18.04/20.04 con ROS2 Foxy**

## Características

- ✅ Soporte para múltiples cámaras (sensor_id 0 y 1)
- ✅ Parámetros configurables (resolución, framerate, sensor_mode)
- ✅ Publicación en tópicos ROS2 estándar
- ✅ Compatible con RViz para visualización
- ✅ GStreamer pipeline optimizado para Jetson Nano

## Instalación

Coloca este paquete en el directorio `src/` de tu workspace ROS2:

```bash
cd ~/MARVIN/marvin_real
colcon build
source install/setup.bash
```

## Uso

### Lanzar ambas cámaras

```bash
ros2 launch marvincar_camera csi_cameras_launch.py
```

### Lanzar con parámetros personalizados

```bash
ros2 launch marvincar_camera csi_cameras_launch.py \
  capture_width:=1280 \
  capture_height:=720 \
  framerate:=30
```

### Ejecución manual de un nodo

```bash
ros2 run marvincar_camera csi_camera_node --ros-args \
  -p sensor_id:=0 \
  -p capture_width:=1920 \
  -p capture_height:=1080 \
  -p framerate:=20
```

## Tópicos Publicados

- `/camera_0/image_raw` - Imágenes de la cámara 0 (tipo: `sensor_msgs/Image`)
- `/camera_1/image_raw` - Imágenes de la cámara 1 (tipo: `sensor_msgs/Image`)

## Parámetros

| Parámetro | Tipo | Valor por defecto | Descripción |
|-----------|------|------------------|-------------|
| `sensor_id` | int | 0 | ID del sensor CSI (0 o 1) |
| `sensor_mode` | int | 0 | Modo del sensor |
| `capture_width` | int | 1920 | Ancho de captura en píxeles |
| `capture_height` | int | 1080 | Alto de captura en píxeles |
| `framerate` | int | 20 | Framerate en Hz |

## Visualización en RViz

1. Abre RViz: `rviz2`
2. Agrega un plugin **Image** a través de **Panels → Add new panel → Image**
3. Configura el tópico en el panel Image:
   - `/camera_0/image_raw` para la cámara izquierda
   - `/camera_1/image_raw` para la cámara derecha

## Estructura del Paquete

```
marvincar_camera/
├── marvincar_camera/
│   ├── __init__.py
│   └── csi_camera_node.py        # Nodo principal
├── launch/
│   └── csi_cameras_launch.py     # Launch file para ambas cámaras
├── package.xml
├── setup.py
└── README.md
```

## Notas

- Las cámaras deben estar correctamente conectadas a los puertos CSI del Jetson Nano
- GStreamer y `opencv-python` deben estar instalados en el Docker
- El nodo utiliza `sensor_id=0` y `sensor_id=1` para diferenciar las cámaras

## Autor

MARVIN Team - Proyecto de Robótica Autónoma