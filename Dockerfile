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
    ros-foxy-cv-bridge \
    ros-foxy-sensor-msgs

# Install Python dependencies for camera support
RUN pip3 install --upgrade pip && \
    pip3 install opencv-python opencv-contrib-python

WORKDIR /root/marvin/marvin_real

