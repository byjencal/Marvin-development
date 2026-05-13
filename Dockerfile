FROM yahboomtechnology/ros-foxy:3.5.3

WORKDIR /root/marvin

COPY . .

COPY ./configurations/.bashrc /root/.bashrc

WORKDIR /root/marvin/marvin_real

RUN find . -type f -exec touch {} +

RUN rm -rf build install log || true

# Instalar GStreamer para soporte de cámaras CSI/nvarguscamerasrc
RUN apt-get update && \
    apt-get install -y \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    libgstreamer1.0-0 && \
    rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]

