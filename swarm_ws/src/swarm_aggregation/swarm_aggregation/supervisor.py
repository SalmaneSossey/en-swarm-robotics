import csv
import time
from pathlib import Path

import numpy as np
import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node


class Supervisor(Node):
    def __init__(self) -> None:
        super().__init__("swarm_aggregation_supervisor")
        self.declare_parameter("n", 10)
        self.declare_parameter("output_csv", "sigma2.csv")
        self.n = int(self.get_parameter("n").value)
        self.output_csv = Path(str(self.get_parameter("output_csv").value))
        self.positions = np.zeros((self.n, 2), dtype=float)
        self.received = [False] * self.n
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
        self.writer.writerow(["t", "sigma2", "center_x", "center_y"])
        self.create_timer(1.0, self.compute_sigma2)
        self.get_logger().info(f"Logging sigma2 for {self.n} robots to {self.output_csv}.")

    def odom_callback(self, msg: Odometry, index: int) -> None:
        self.positions[index, 0] = msg.pose.pose.position.x
        self.positions[index, 1] = msg.pose.pose.position.y
        self.received[index] = True

    def compute_sigma2(self) -> None:
        if not all(self.received):
            return
        center = self.positions.mean(axis=0)
        sigma2 = float(np.mean(np.sum((self.positions - center) ** 2, axis=1)))
        elapsed = time.monotonic() - self.t0
        self.writer.writerow([f"{elapsed:.2f}", f"{sigma2:.4f}", f"{center[0]:.4f}", f"{center[1]:.4f}"])
        self.csv_file.flush()
        self.get_logger().info(f"t={elapsed:.1f}s sigma2={sigma2:.3f}")

    def destroy_node(self) -> bool:
        if hasattr(self, "csv_file") and not self.csv_file.closed:
            self.csv_file.close()
        return super().destroy_node()


def main() -> None:
    rclpy.init()
    node = Supervisor()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
