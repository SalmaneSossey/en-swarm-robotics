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
cd /home/salmane/Tps/swarm_robotics/swarm_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch swarm_aggregation swarm.launch.py n:=10 arena:=1.2
```

Terminal 2:

```bash
cd /home/salmane/Tps/swarm_robotics/swarm_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch swarm_aggregation aggregation.launch.py n:=10
```

Terminal 3:

```bash
cd /home/salmane/Tps/swarm_robotics/swarm_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
rm -f sigma2.csv sigma2.png
ros2 service call /unpause_physics std_srvs/srv/Empty {}
ros2 run swarm_aggregation supervisor --ros-args -p n:=10 -p output_csv:=sigma2.csv
```

After at least 5 minutes:

```bash
ros2 run swarm_aggregation plot_sigma2
ros2 run swarm_aggregation analyze_sigma2 sigma2.csv
```

For the TP7 parametric study, repeat with `n:=3`, `n:=10`, `n:=20`, and `n:=30`, save each tconv in a CSV like:

```csv
N,run,tconv
10,1,1.00
10,2,3.00
```

Then plot:

```bash
ros2 run swarm_aggregation plot_tconv tconv_summary.csv --output tconv_by_n.png
```

## TP6 Quick Run

Terminal 1:

```bash
cd /home/salmane/Tps/swarm_robotics/swarm_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch swarm_meta meta_swarm.launch.py n:=6
```

Terminal 2:

```bash
cd /home/salmane/Tps/swarm_robotics/swarm_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch swarm_meta controllers.launch.py n:=6 algorithm:=gwo adapted:=true
```

Terminal 3:

```bash
cd /home/salmane/Tps/swarm_robotics/swarm_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run swarm_meta evaluator --ros-args -p n:=6 -p output_csv:=tp6_metrics.csv
```

Comparison requested in TP6:

```bash
# Run 1: adapted GWO with DVC
ros2 launch swarm_meta controllers.launch.py n:=6 algorithm:=gwo adapted:=true
ros2 run swarm_meta evaluator --ros-args -p n:=6 -p output_csv:=tp6_adapted.csv

# Run 2: original-style GWO without the signed acceleration bound
ros2 launch swarm_meta controllers.launch.py n:=6 algorithm:=gwo adapted:=false
ros2 run swarm_meta evaluator --ros-args -p n:=6 -p output_csv:=tp6_original.csv

ros2 run swarm_meta plot_metrics tp6_adapted.csv tp6_original.csv --labels adapted,original --output tp6_comparison.png
```

## Debug Checks

```bash
ros2 topic list | grep robot_0
ros2 topic echo /robot_0/odom --once
ros2 topic echo /robot_0/scan --once
ros2 topic echo /robot_0/cmd_vel --once
ros2 topic echo /swarm/best --once
```

## Deliverables Status

- TP6 code, launch files, Gazebo arena, adapted/original controller switch, evaluator, and plotting helper are implemented.
- TP7 code, launch files, bounded Gazebo arena, supervisor, sigma2 plotter, tconv analyzer, and tconv plotter are implemented.
- Report drafts are in `docs/TP6_REPORT.md` and `docs/TP7_REPORT.md`.
- The MP4 videos must still be recorded manually from Gazebo, because screen recording is a desktop action.
