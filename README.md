# ROS RC car pwm publisher
This project demonstrates a basic **ROS pwm node publisher** setup using Python.

## 🧱 Project Structure

ros_ws/  
├── build/  
│ ├── control_pkg  
│ └── rc_pwm_pkg  
├── install/  
├── log/  
├── src/  
│ ├── control_pkg  
│ └── rc_pwm_pkg  
└── README.md  

## ⚙️ Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Python 3

## 📦 Installation

1. Clone the repository into your catkin workspace:

```bash
git clone https://github.com/AimChayakorn/raspicar-wheel-control.git

```

2. Export Discovery server and ROS setup
```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=10
export ROS_DISCOVERY_SERVER=127.0.0.1:11811
```

2.  Build the workspace

```bash
source install/setup.bash
colcon build
```

3. Start fastdds server

```bash
fastdds discovery --server-id 0
```

4. Start controller node
```bash
ros2 run control_pkg control_node
```

5. Start pwm publisher node

```bash
ros2 run control_pkg pwm_node
```