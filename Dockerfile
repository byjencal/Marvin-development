# Usamos la imagen oficial de NVIDIA para Jetson con Foxy preinstalado
FROM dustynv/ros:foxy-ros-base-l4t-r32.7.1

# 1. Eliminar la llave caducada de ROS y descargar la oficial actualizada
RUN apt-key del F42ED6FBAB17C654 || true && \
    (apt-get update || true) && \
    apt-get install -y curl && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add -

# 2. Instalar OpenCV y el puente de ROS 2
RUN apt-get update && apt-get install -y \
    python3-opencv \
    ros-foxy-cv-bridge \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/marvin

# 3. Copiar el código fuente y configuraciones
COPY . .
COPY ./configurations/.bashrc /root/.bashrc

WORKDIR /root/marvin/marvin_ws

# 4. Sincronizar relojes y limpiar builds antiguos
RUN find . -type f -exec touch {} +
RUN rm -rf build install log || true

CMD ["/bin/bash"]