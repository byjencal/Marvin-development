# Usamos la imagen oficial de NVIDIA para Jetson con Foxy preinstalado
FROM dustynv/ros:foxy-ros-base-l4t-r32.7.1

# 1. Instalar OpenCV y el puente de ROS 2 (GStreamer ya viene incluido de fábrica)
RUN apt-get update && apt-get install -y \
    python3-opencv \
    ros-foxy-cv-bridge \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/marvin

# 2. Copiar el código fuente y configuraciones
COPY . .
COPY ./configurations/.bashrc /root/.bashrc

WORKDIR /root/marvin/marvin_ws

# 3. Sincronizar relojes y limpiar builds antiguos
RUN find . -type f -exec touch {} +
RUN rm -rf build install log || true

CMD ["/bin/bash"]