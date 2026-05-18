# Usamos la imagen oficial de NVIDIA para Jetson con Foxy preinstalado
FROM dustynv/ros:foxy-ros-base-l4t-r32.7.1

# 1. Sobrescribir físicamente el archivo de la llave en todas las rutas del sistema
RUN apt-get update || true && apt-get install -y curl && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /etc/apt/trusted.gpg.d/ros2-latest.gpg && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | apt-key add -

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