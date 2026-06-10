#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Configurando workspace para Jetson Nano..."
echo "Se ignoraran paquetes de interfaz, navegacion, descripcion y vision."

touch "$ROOT_DIR/marvin_ws/src/marvincar_ctrl/COLCON_IGNORE"
echo "COLCON_IGNORE creado en marvin_ws/src/marvincar_ctrl"

touch "$ROOT_DIR/marvin_ws/src/marvincar_nav/COLCON_IGNORE"
echo "COLCON_IGNORE creado en marvin_ws/src/marvincar_nav"

touch "$ROOT_DIR/marvin_ws/src/marvincar_description/COLCON_IGNORE"
echo "COLCON_IGNORE creado en marvin_ws/src/marvincar_description"

touch "$ROOT_DIR/marvin_ws/src/marvincar_vision/COLCON_IGNORE"
echo "COLCON_IGNORE creado en marvin_ws/src/marvincar_vision"

echo "Listo. La Jetson compilara solo los paquetes de hardware/base correspondientes."
