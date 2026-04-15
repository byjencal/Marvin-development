FROM yahboomtechnology/ros-foxy:3.5.3
WORKDIR /root/marvin
COPY . .
COPY ./configurations/.bashrc ..

# Install OpenCV for camera support
RUN pip install opencv-python

WORKDIR /root/marvin/marvin_real

