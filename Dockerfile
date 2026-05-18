# Usamos la imagen oficial de NVIDIA para Jetson con Foxy preinstalado
FROM dustynv/ros:foxy-ros-base-l4t-r32.7.1

# 1. Renovar la llave de seguridad (GPG) de ROS 2 que expiró
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F42ED6FBAB17C654 || \
    (apt-get update || true && apt-get install -y curl && curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | apt-key add -)

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