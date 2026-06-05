# TP6 Notes

Chosen algorithm: Grey Wolf Optimization (GWO).

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
