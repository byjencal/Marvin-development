#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Configurando workspace para Laptop Ubuntu 20.04..."
echo "Se ignoraran paquetes de hardware, drivers y bringup del robot fisico."

touch "$ROOT_DIR/marvin_ws/src/marvincar_base_node/COLCON_IGNORE"
echo "COLCON_IGNORE creado en marvin_ws/src/marvincar_base_node"

touch "$ROOT_DIR/marvin_ws/src/marvincar_bringup/COLCON_IGNORE"
echo "COLCON_IGNORE creado en marvin_ws/src/marvincar_bringup"

touch "$ROOT_DIR/marvin_ws/src/marvin_lidar/COLCON_IGNORE"
echo "COLCON_IGNORE creado en marvin_ws/src/marvin_lidar"

touch "$ROOT_DIR/marvin_ws/src/marvincar_laser/COLCON_IGNORE"
echo "COLCON_IGNORE creado en marvin_ws/src/marvincar_laser"

echo "Listo. La laptop compilara solo los paquetes de control, visualizacion y navegacion."
