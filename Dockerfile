FROM yahboomtechnology/ros-foxy:3.5.3
WORKDIR /root/marvin
COPY . .
COPY ./configurations/.bashrc ..

# Install OpenCV for camera support (use pip3 for Python 3)
RUN pip3 install opencv-python

WORKDIR /root/marvin/marvin_real

