import csv
import time
from pathlib import Path

import numpy as np
import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node


class Evaluator(Node):
    def __init__(self) -> None:
        super().__init__("swarm_meta_evaluator")
        self.declare_parameter("n", 6)
        self.declare_parameter("target_x", 4.0)
        self.declare_parameter("target_y", 0.0)
        self.declare_parameter("output_csv", "tp6_metrics.csv")
        self.n = int(self.get_parameter("n").value)
        self.target = np.array(
            [
                float(self.get_parameter("target_x").value),
                float(self.get_parameter("target_y").value),
            ],
            dtype=float,
        )
        self.output_csv = Path(str(self.get_parameter("output_csv").value))
        self.positions = np.zeros((self.n, 2), dtype=float)
        self.last_seen = np.zeros(self.n, dtype=float)
        for index in range(self.n):
            self.create_subscription(
                Odometry,
                f"/robot_{index}/odom",
                lambda msg, idx=index: self.odom_callback(msg, idx),
                10,
            )
        self.t0 = time.monotonic()
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        self.csv_file = self.output_csv.open("w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(["t", "mean_center_fitness", "survival_percent", "center_x", "center_y"])
        self.create_timer(1.0, self.compute_metrics)
        self.get_logger().info(f"Logging TP6 metrics to {self.output_csv}.")

    def odom_callback(self, msg: Odometry, index: int) -> None:
        self.positions[index, 0] = msg.pose.pose.position.x
        self.positions[index, 1] = msg.pose.pose.position.y
        self.last_seen[index] = time.monotonic()

    def compute_metrics(self) -> None:
        now = time.monotonic()
        alive = now - self.last_seen < 3.0
        if not alive.any():
            return
        center = self.positions[alive].mean(axis=0)
        mean_center_fitness = float(np.linalg.norm(center - self.target))
        survival_percent = 100.0 * float(np.mean(alive))
        elapsed = now - self.t0
        self.writer.writerow(
            [
                f"{elapsed:.2f}",
                f"{mean_center_fitness:.4f}",
                f"{survival_percent:.1f}",
                f"{center[0]:.4f}",
                f"{center[1]:.4f}",
            ]
        )
        self.csv_file.flush()
        self.get_logger().info(
            f"t={elapsed:.1f}s center_fitness={mean_center_fitness:.3f} survival={survival_percent:.1f}%"
        )

    def destroy_node(self) -> bool:
        if hasattr(self, "csv_file") and not self.csv_file.closed:
            self.csv_file.close()
        return super().destroy_node()


def main() -> None:
    rclpy.init()
    node = Evaluator()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
