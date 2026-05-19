FROM dustynv/ros:foxy-ros-base-l4t-r32.7.1

# 1. El parche de la llave GPG de ROS 2
RUN apt-key del F42ED6FBAB17C654 || true && \
    (apt-get update || true) && \
    apt-get install -y curl gnupg2 ca-certificates && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /etc/apt/trusted.gpg.d/ros2-latest.gpg && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | apt-key add -

# 2. Desbloquear los repositorios oficiales de NVIDIA (Jetson OTA)
RUN curl -sSL https://repo.download.nvidia.com/jetson/jetson-ota-public.asc | apt-key add - && \
    echo "deb https://repo.download.nvidia.com/jetson/common r32.7 main" > /etc/apt/sources.list.d/nvidia-l4t-apt-source.list && \
    echo "deb https://repo.download.nvidia.com/jetson/t210 r32.7 main" >> /etc/apt/sources.list.d/nvidia-l4t-apt-source.list

# 3. Instalar CUDA 10.2, OpenCV y Git sin bloqueos
RUN apt-get update && apt-get install -y \
    cuda-toolkit-10-2 \
    python3-opencv \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/marvin

# 4. Copiar tu código
COPY . .
COPY ./configurations/.bashrc /root/.bashrc

WORKDIR /root/marvin/marvin_ws

# 5. Descargar el código fuente de cv_bridge oficial
RUN git clone -b foxy https://github.com/ros-perception/vision_opencv.git src/vision_opencv

# 6. Sincronizar relojes
RUN find . -type f -exec touch {} +
RUN rm -rf build install log || true

CMD ["/bin/bash"]