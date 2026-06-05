# TP6 Report Draft

## Algorithm

The selected metaheuristic is Grey Wolf Optimization. Each robot is an omega wolf, while the three best currently known robots are alpha, beta, and delta. Fitness is the distance to the target:

```text
f(x_i) = ||x_i - x_target||
```

Each robot publishes its current position and fitness on `/swarm/best`. Every controller instance keeps the most recent swarm records and selects the three lowest-fitness positions as `y_alpha`, `y_beta`, and `y_delta`.

## Adapted Velocity Equation

For robot position `x[k]` and velocity reference `u[k]`:

```text
u[k+1] = omega u[k]
       + sum_l (c_hat / 3) r_l sgn(y_l[k] - x[k])
       + c_obs r_obs sgn(F_obs)

l in {alpha, beta, delta}
c_hat = A_plus dt / sqrt(2)
omega = 1 - A_plus dt / U
U = min(U_nominal, alpha_dvc s_nearest)
```

The `sgn` term bounds the acceleration contribution from each leader. The dynamic velocity constraint uses the closest LiDAR range `s_nearest` to reduce the maximum allowed speed near obstacles. The obstacle term is a repulsive vector computed from the nearest LiDAR obstacle direction.

## ROS 2 Pipeline

```text
Gazebo TurtleBot3
  -> /robot_i/odom and /robot_i/scan
  -> swarm_robot.py
  -> /swarm/best fitness exchange
  -> GWO leader selection
  -> DVC and obstacle avoidance
  -> /robot_i/cmd_vel
```

## Evaluation

The evaluator logs:

```text
t, mean_center_fitness, survival_percent, center_x, center_y
```

The assignment asks for 10 runs of 15 minutes. For each run, save:

```text
tp6_adapted_run_<k>.csv
tp6_original_run_<k>.csv
```

Then plot individual runs or comparison curves:

```bash
ros2 run swarm_meta plot_metrics tp6_adapted.csv tp6_original.csv --labels adapted,original --output tp6_comparison.png
```

## Discussion

The adapted GWO version is expected to be safer near obstacles because the signed acceleration bounds prevent large jumps in velocity reference, and DVC lowers `U` when the nearest obstacle is close. The original-style version can move more aggressively toward leaders, but it is less compatible with physical robot limits and can produce worse survival in dense obstacle areas.

## Deliverables

- Code: `swarm_meta`
- Launch files: `meta_swarm.launch.py`, `controllers.launch.py`
- Curves: `tp6_comparison.png` plus 10-run CSVs
- Video: record up to 30 seconds of Gazebo during the adapted GWO run
