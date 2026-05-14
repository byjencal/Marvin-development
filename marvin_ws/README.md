# MARVIN Real Robot (Jetson Nano)

This guide covers the setup and execution steps for the MARVIN robot using a Jetson Nano and ROS2 Foxy.

## Hardware & Software Requirements
- **Hardware:** Jetson Nano Developer Kit
- **Robot OS:** Ubuntu 18.04 (Bionic) or 20.04 (Focal) with Docker.
- **PC OS:** Ubuntu 20.04 LTS with ROS2 Foxy.

---

## PC Setup (Remote Control & Visualization)

1.  **Install ROS2 Foxy:**
    Follow instructions: [Ubuntu Install Debians](https://docs.ros.org/en/foxy/Installation/Ubuntu-Install-Debians.html)
    
    ```sh
    echo "source /opt/ros/foxy/setup.bash" >> ~/.bashrc
    ```

2.  **Configure Environment:**
    ```sh
    echo "export ROS_DOMAIN_ID=0" >> ~/.bashrc
    source ~/.bashrc
    ```

3.  **Install Dependencies:**
    ```sh
    sudo apt install python3-colcon-common-extensions
    sudo apt install ros-foxy-navigation2 ros-foxy-nav2-bringup
    ```

4.  **Clone Repository:**
    ```sh
    git clone https://github.com/RAMEL-ESPOL/MARVIN.git
    cd MARVIN/marvin_real
    colcon build
    source install/setup.bash
    ```

---

## Jetson Nano Setup

1.  **Connect to Jetson Nano:**
    Connect to the same WiFi network and SSH into the robot (check IP with `hostname -I` on the robot):
    ```sh
    ssh marvin@<JETSON_IP_ADDRESS>
    ```

2.  **Set Date & Time (CRITICAL):**
    Always set the date/time after booting:
    ```sh
    # Example format: YYYYMMDD
    sudo date +%Y%m%d -s "20240129" 
    # Example format: HH:MM:SS
    sudo date +%T -s "10:00:00"
    ```

3.  **Docker Setup:**
    Navigate to the project folder and build the Docker image:
    ```sh
    cd /MARVIN
    sudo docker build . -t marvin:latest
    ```

4.  **Run Container:**
    ```sh
    sudo docker run -it --net=host \
      --device=/dev/input/event0 --device=/dev/input/event1 --device=/dev/input/event2 \
      --device=/dev/input/js0 --device=/dev/myserial --device=/dev/rplidar \
      --env="DISPLAY" --env="QT_X11_NO_MITSHM=1" \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      marvin:latest /bin/bash
    ```

---

## Execution Process (Inside Docker Container)

**Note:** Inside the Docker container, run `source install/setup.bash` in every new terminal.

### 1. Build Package
```sh
colcon build
source install/setup.bash
```

### 2. Launch Control & LiDAR
```sh
ros2 launch marvincar_bringup marvincar_bringup_launch.py
```

### 3. Launch Extra LiDAR Nodes (New Terminal)
```sh
# Access container first: docker exec -it <container_name> /bin/bash
source install/setup.bash
ros2 launch marvin_lidar ld19.launch.py
```

---

## Operations (From PC)

### 1. View Mapping (Real-time)
```sh
ros2 launch marvincar_nav view_map_launch.py
```

### 2. Start SLAM
```sh
ros2 launch marvincar_nav mapping_launch.py
```
*   Drive the robot to map the area.
*   Save the map using **SlamToolboxPlugin** in Rviz as "marvincar".

### 3. Navigation
```sh
ros2 launch marvincar_nav navigation_dwa_launch.py
```
*   Use **2D Pose Estimate** to set initial position.
*   Use **2D Goal Pose** to send navigation commands.
