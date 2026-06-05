# Swarm Robotics TP6-TP7

Separate ROS 2 workspace for the swarm robotics assignments:

- `swarm_meta`: TP6 bio-inspired metaheuristic swarm control, implemented with Grey Wolf Optimization plus dynamic velocity constraints.
- `swarm_aggregation`: TP7 decentralized BEECLUST-style aggregation and convergence measurement.

These packages intentionally live outside the BCR Arm TP3-TP5 repository.

## Dependencies

```bash
sudo apt update
sudo apt install -y \
  ros-humble-turtlebot3* \
  ros-humble-turtlebot3-gazebo \
  ros-humble-gazebo-ros-pkgs

echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc
source ~/.bashrc

/usr/bin/python3 -m pip install --user numpy matplotlib pandas
```

## Build

```bash
cd /home/salmane/Tps/swarm_robotics/swarm_ws
source /opt/ros/humble/setup.bash
colcon build --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
source install/setup.bash
```

## TP7 Quick Run

Terminal 1:

```bash
ros2 launch swarm_aggregation swarm.launch.py n:=10
```

Terminal 2:

```bash
ros2 launch swarm_aggregation aggregation.launch.py n:=10
```

Terminal 3:

```bash
ros2 run swarm_aggregation supervisor n:=10
```

## TP6 Quick Run

Terminal 1:

```bash
ros2 launch swarm_meta meta_swarm.launch.py n:=6
```

Terminal 2:

```bash
ros2 launch swarm_meta controllers.launch.py n:=6 algorithm:=gwo
```

Terminal 3:

```bash
ros2 run swarm_meta evaluator --ros-args -p n:=6 -p output_csv:=tp6_metrics.csv
```
