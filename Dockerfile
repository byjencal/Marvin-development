# Usamos la imagen oficial de NVIDIA para Jetson con Foxy preinstalado
FROM dustynv/ros:foxy-ros-base-l4t-r32.7.1

# 1. El parche de la llave GPG (¡Que ya vimos que funciona a la perfección!)
RUN apt-get update || true && apt-get install -y curl && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /etc/apt/trusted.gpg.d/ros2-latest.gpg && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | apt-key add -

# 2. Instalar herramientas del sistema y OpenCV estándar (cv_bridge lo haremos a mano)
RUN apt-get update && apt-get install -y \
    python3-opencv \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/marvin

# 3. Copiar el código fuente y configuraciones
COPY . .
COPY ./configurations/.bashrc /root/.bashrc

WORKDIR /root/marvin/marvin_ws

# 4. Clonar el código fuente de cv_bridge (rama foxy) directamente a tu workspace
RUN git clone -b foxy https://github.com/ros-perception/vision_opencv.git src/vision_opencv

# 5. Sincronizar relojes y limpiar builds antiguos
RUN find . -type f -exec touch {} +
RUN rm -rf build install log || true

CMD ["/bin/bash"]