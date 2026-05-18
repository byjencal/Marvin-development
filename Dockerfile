FROM yahboomtechnology/ros-foxy:3.5.3

# 1. Instalar dependencias del sistema (GStreamer y OpenCV)
# Usamos un solo RUN y limpiamos la caché al final para que la imagen no pese gigabytes extra
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

# 2. Copiar el código fuente
COPY . .

# 3. Copiar configuraciones del entorno
COPY ./configurations/.bashrc /root/.bashrc

WORKDIR /root/marvin/marvin_ws

# 4. Sincronizar relojes y limpiar builds antiguos del host
RUN find . -type f -exec touch {} +
RUN rm -rf build install log || true

# (Opcional) 5. Compilar el workspace automáticamente al crear la imagen
# RUN /bin/bash -c "source /opt/ros/foxy/setup.bash && colcon build"

CMD ["/bin/bash"]