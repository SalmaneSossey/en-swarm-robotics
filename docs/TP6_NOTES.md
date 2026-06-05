# TP6 Notes

Chosen algorithm: Grey Wolf Optimization (GWO), adapted for physical TurtleBot3 robots.

Robot state:

```text
x_i[k] in R^2
u_i[k] in R^2
fitness_i = ||x_i - x_target||
```

At each controller step, robots publish a fitness snapshot on `/swarm/best`.
Each robot chooses the three lowest-fitness records as leaders:

```text
y_alpha, y_beta, y_delta
```

Adapted velocity update:

```text
u[k+1] = omega u[k]
       + sum_{l in {alpha,beta,delta}} (c_hat / 3) r_l sgn(y_l[k] - x[k])
       + c_obs r_obs sgn(F_obs)
```

Calibration:

```text
c_hat = A_plus * dt / sqrt(2)
omega = 1 - A_plus * dt / U
U = min(U_nominal, alpha_dvc * nearest_lidar_range)
```

The `adapted:=false` launch option disables `sgn(...)` in the leader attraction term for the comparison requested in TP6.

ROS 2 pipeline:

```text
/robot_i/odom + /robot_i/scan
  -> swarm_robot.py
  -> /swarm/best fitness exchange
  -> GWO leader selection alpha/beta/delta
  -> DVC velocity/obstacle recalibration
  -> /robot_i/cmd_vel
  -> Gazebo
```

Implemented files:

- `swarm_meta/swarm_robot.py`: GWO controller with signed acceleration and DVC.
- `launch/meta_swarm.launch.py`: starts Gazebo with 6 TurtleBot3 and the obstacle arena.
- `launch/controllers.launch.py`: starts one controller per namespace.
- `swarm_meta/evaluator.py`: writes mean center fitness and survival percentage.
- `swarm_meta/plot_metrics.py`: plots fitness/survival curves and adapted-vs-original comparisons.

Recommended comparison:

```bash
ros2 launch swarm_meta controllers.launch.py n:=6 algorithm:=gwo adapted:=true
ros2 run swarm_meta evaluator --ros-args -p n:=6 -p output_csv:=tp6_adapted.csv

ros2 launch swarm_meta controllers.launch.py n:=6 algorithm:=gwo adapted:=false
ros2 run swarm_meta evaluator --ros-args -p n:=6 -p output_csv:=tp6_original.csv

ros2 run swarm_meta plot_metrics tp6_adapted.csv tp6_original.csv --labels adapted,original --output tp6_comparison.png
```
