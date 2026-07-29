# 1. Dockerfile para construir la imagen de Docker para el proyecto Marvin en Jetson Nano con ROS 2 Foxy
FROM dustynv/ros:foxy-ros-base-l4t-r32.7.1

# 2. El parche de la llave GPG de ROS 2
RUN apt-key del F42ED6FBAB17C654 || true && \
    (apt-get update || true) && \
    apt-get install -y curl gnupg2 ca-certificates && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /etc/apt/trusted.gpg.d/ros2-latest.gpg && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | apt-key add -

# 3. Desbloquear los repositorios oficiales de NVIDIA (Jetson OTA)
RUN curl -sSL https://repo.download.nvidia.com/jetson/jetson-ota-public.asc | apt-key add - && \
    echo "deb https://repo.download.nvidia.com/jetson/common r32.7 main" > /etc/apt/sources.list.d/nvidia-l4t-apt-source.list && \
    echo "deb https://repo.download.nvidia.com/jetson/t210 r32.7 main" >> /etc/apt/sources.list.d/nvidia-l4t-apt-source.list

# 4. Instalar CUDA 10.2, OpenCV y Git sin bloqueos
RUN apt-get update && apt-get install -y \
    cuda-toolkit-10-2 \
    python3-opencv \
    git \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 5. Instalar dependencias de Python
RUN pip3 install depthai pyserial smbus2

# 6. Crear directorio de trabajo
WORKDIR /root/marvin

# 7.
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# 8. Configurar CycloneDDS
ENV CYCLONEDDS_URI=file:///root/marvin/marvin_ws/shared_config/cyclonedds.xml

# 9. Copiar tu código
COPY . .

# 10. Copiar el archivo .bashrc personalizado
RUN ln -sf /root/marvin/marvin_ws/configurations/.bashrc /root/.bashrc

# 11. Configurar el entorno de ROS 2
WORKDIR /root/marvin/marvin_ws

# 12. Instalar dependencias de Python desde setup.py
RUN cd dependencies/py_install && python3 setup.py install

# Descargar el código fuente de cv_bridge oficial
# RUN git clone -b foxy https://github.com/ros-perception/vision_opencv.git src/vision_opencv

# 13. Sincronizar relojes
RUN find . -type f -exec touch {} +

# 14. Borrar los directorios de compilación para ahorrar espacio
RUN rm -rf build install log || true

# 15. Establecer el comando por defecto
CMD ["/bin/bash"]
