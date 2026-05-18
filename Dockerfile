FROM yahboomtechnology/ros-foxy:3.5.3

# 1. Renovar la llave de seguridad (GPG) de ROS 2 que expiró
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F42ED6FBAB17C654 || \
    (apt-get update || true && apt-get install -y curl && curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | apt-key add -)

# 2. Instalar dependencias del sistema (GStreamer y OpenCV)
RUN apt-get update && apt-get install -y \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    python3-opencv \
    ros-foxy-cv-bridge \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/marvin

# 3. Copiar el código fuente
COPY . .

# 4. Copiar configuraciones del entorno
COPY ./configurations/.bashrc /root/.bashrc

WORKDIR /root/marvin/marvin_ws

# 5. Sincronizar relojes y limpiar builds antiguos del host
RUN find . -type f -exec touch {} +
RUN rm -rf build install log || true

CMD ["/bin/bash"]