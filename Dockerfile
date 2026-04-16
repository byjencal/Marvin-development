FROM yahboomtechnology/ros-foxy:3.5.3
WORKDIR /root/marvin
COPY . .
COPY ./configurations/.bashrc ..

# Update package lists
RUN apt-get update

# Install system-level camera and video dependencies
RUN apt-get install -y \
    libv4l-dev \
    v4l-utils \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad

# Install Python dependencies for camera support
RUN pip3 install --upgrade pip && \
    pip3 install opencv-python opencv-contrib-python

WORKDIR /root/marvin/marvin_real

