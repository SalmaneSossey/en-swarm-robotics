# TP7 Notes

Algorithm: simplified BEECLUST.

State machine:

- `MOVING`: publish forward velocity `0.20 m/s`.
- `STOPPED`: if LiDAR detects a neighbor or wall closer than `0.50 m`, stop for `5 s`.
- `TURNING`: after stopping, choose a random angle in `[0, 2pi]`, turn at `0.50 rad/s`, then return to `MOVING`.

Convergence metric:

```text
x_bar(t) = (1 / N) sum_i x_i(t)
sigma2(t) = (1 / N) sum_i ||x_i(t) - x_bar(t)||^2
```

Run `supervisor` to write `sigma2.csv`, then run `plot_sigma2` to produce `sigma2.png`.
