# TP7 Report Draft

## Concept Answers

Question 1.1: A decentralized swarm is robust and scalable because each robot uses local sensing instead of relying on one supervisor. If one robot fails, the others continue.

Question 1.2: Emergence means a global behavior appears from local rules. Biological examples include ant trail formation and honeybee aggregation. Robotic examples include swarm aggregation and collective area coverage.

Question 3.1: Namespaces are required so each robot has its own `/robot_i/scan`, `/robot_i/odom`, and `/robot_i/cmd_vel`. Without namespaces, topics collide and controllers cannot target one robot cleanly.

Question 3.2: Use `ros2 topic list | grep robot_0` and compare `ros2 topic echo /robot_0/scan --once` with another namespace such as `/robot_1/scan`.

Question 4.1: In `MOVING`, the robot moves forward. If LiDAR detects a close object, it switches to `STOPPED`. In `STOPPED`, it waits until the stop timer expires. Then it switches to `TURNING`, rotates by a random angle, and returns to `MOVING`.

Question 4.3: Testing with one robot first verifies topic names, LiDAR callbacks, and velocity commands before debugging multi-robot interactions.

Question 4.4: A small `dmin` avoids stopping for distant objects. If `dmin` is too large, robots stop too often and exploration slows.

Question 5.1: After a few minutes, robots tend to form local groups. Robots remain stopped longer in denser areas, so clusters become attractive without any global communication.

Question 6.1: The supervisor waits for every odometry topic so sigma2 is computed from the whole swarm, not from a partial set.

Question 6.2: The behavior is decentralized, but the metric computation is centralized for measurement only. A decentralized estimate could use local communication and consensus between neighboring robots.

Question 7.1: The curve is usually noisy and step-like, not perfectly monotonic, because robots keep moving and random turns can temporarily increase spatial variance.

Question 7.2: More robots can converge faster because encounters are more frequent, but too many robots can also cause congestion.

Question 7.3: Yes. Beyond some N, additional robots may no longer improve convergence and can degrade it through crowding and collisions.

Question 8.1: The swarm aggregates because close encounters cause longer stops. Dense areas therefore retain robots longer than sparse areas.

Question 8.2: Aggregation is emergent because no robot knows the swarm center or global objective; the group forms from local LiDAR-triggered state transitions.

Question 8.3: Removing 20 percent of robots should not stop the algorithm. Aggregation may become slower, but the remaining robots still follow the same local rules.

Question 8.4: BEECLUST is more fault tolerant and scalable than a central controller, but a central controller can produce tighter and more predictable formations. BEECLUST is simpler per robot but harder to tune experimentally.

Question 8.5: Two useful extensions are a light gradient so robots bias aggregation toward an external stimulus, and local communication so robots can share short-range density or waiting-time information.

## Pipeline

```text
/robot_i/scan
  -> MOVING/STOPPED/TURNING state machine
  -> /robot_i/cmd_vel
  -> Gazebo
  -> /robot_i/odom
  -> supervisor.py
  -> sigma2.csv
  -> sigma2.png and tconv(N)
```

## Current Validated Result

For `N=10`, `arena:=1.2`, threshold `sigma2 < 1.0` held for 10 seconds:

```text
rows=245
duration_s=245.04
first_sigma2=0.7913
last_sigma2=0.8074
min_sigma2=0.7848 at 50.01s
max_sigma2=0.8095 at 244.04s
mean_sigma2=0.7938
tconv=1.00s
```

## Remaining Experimental Table

Run 3 simulations of 5 minutes for each N:

```text
N in {3, 10, 20, 30}
```

Save the extracted convergence times in:

```csv
N,run,tconv
3,1,not_reached
10,1,1.00
```

Then generate the error-bar curve:

```bash
ros2 run swarm_aggregation plot_tconv tconv_summary.csv --output tconv_by_n.png
```
