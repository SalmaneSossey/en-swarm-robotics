# TP7 Notes

Algorithm: simplified BEECLUST, implemented as a fully decentralized local state machine.

State machine:

- `MOVING`: publish forward velocity and a small random wandering angular velocity.
- `STOPPED`: if LiDAR detects a neighbor or wall closer than `D_MIN`, stop for `T_STOP` plus a density bonus.
- `TURNING`: after stopping, choose a random angle, turn, then return to `MOVING`.

Tuned simulation parameters:

```text
V_LIN = 0.12 m/s
V_ANG = 0.80 rad/s
D_MIN = 1.00 m
T_STOP = 8.0 s
recommended launch arena = 1.2 m
```

The PDF skeleton uses `v=0.20`, `dmin=0.50`, and `Tstop=5`. The tuned values above were used because the simulated TurtleBot3 LiDAR and collisions produced more stable aggregation inside the bounded arena.

Convergence metric:

```text
x_bar(t) = (1 / N) sum_i x_i(t)
sigma2(t) = (1 / N) sum_i ||x_i(t) - x_bar(t)||^2
```

Run `supervisor` to write `sigma2.csv`, then run `plot_sigma2` to produce `sigma2.png`.

Last validated N=10 run:

```text
rows=245
duration_s=245.04
first_sigma2=0.7913
last_sigma2=0.8074
min_sigma2=0.7848 at 50.01s
max_sigma2=0.8095 at 244.04s
mean_sigma2=0.7938
tconv=1.00s with threshold=1.0 and hold=10s
```

Implemented files:

- `launch/swarm.launch.py`: Gazebo + randomly spawned TurtleBot3 robots in a bounded arena.
- `launch/aggregation.launch.py`: one `aggregation_robot` node per namespace.
- `swarm_aggregation/aggregation_robot.py`: MOVING/STOPPED/TURNING BEECLUST behavior.
- `swarm_aggregation/supervisor.py`: computes and logs sigma2(t).
- `swarm_aggregation/plot_sigma2.py`: creates `sigma2.png`.
- `swarm_aggregation/analyze_sigma2.py`: extracts tconv from `sigma2.csv`.
- `swarm_aggregation/plot_tconv.py`: plots tconv(N) with error bars.
