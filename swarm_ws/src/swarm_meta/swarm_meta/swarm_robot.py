import math
import random
import time
from dataclasses import dataclass

import numpy as np
import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


@dataclass
class SwarmRecord:
    position: np.ndarray
    fitness: float
    stamp: float


def signed_unit(vector: np.ndarray) -> np.ndarray:
    return np.sign(vector)


def yaw_from_quaternion(z: float, w: float) -> float:
    return math.atan2(2.0 * w * z, 1.0 - 2.0 * z * z)


def rotate_2d(vector: np.ndarray, yaw: float) -> np.ndarray:
    c = math.cos(yaw)
    s = math.sin(yaw)
    return np.array([c * vector[0] - s * vector[1], s * vector[0] + c * vector[1]], dtype=float)


class SwarmRobot(Node):
    def __init__(self) -> None:
        super().__init__("swarm_robot")
        self.declare_parameter("robot_id", 0)
        self.declare_parameter("n", 6)
        self.declare_parameter("target_x", 4.0)
        self.declare_parameter("target_y", 0.0)
        self.declare_parameter("dt", 0.1)
        self.declare_parameter("u_max", 0.22)
        self.declare_parameter("a_max", 0.18)
        self.declare_parameter("dvc_alpha", 0.45)
        self.declare_parameter("obstacle_gain", 0.8)
        self.declare_parameter("obstacle_gamma", 2.0)
        self.declare_parameter("adapted", True)

        self.robot_id = int(self.get_parameter("robot_id").value)
        self.n = int(self.get_parameter("n").value)
        self.target = np.array(
            [
                float(self.get_parameter("target_x").value),
                float(self.get_parameter("target_y").value),
            ],
            dtype=float,
        )
        self.dt = float(self.get_parameter("dt").value)
        self.u_max_nominal = float(self.get_parameter("u_max").value)
        self.a_max = float(self.get_parameter("a_max").value)
        self.dvc_alpha = float(self.get_parameter("dvc_alpha").value)
        self.obstacle_gain = float(self.get_parameter("obstacle_gain").value)
        self.obstacle_gamma = float(self.get_parameter("obstacle_gamma").value)
        self.adapted = bool(self.get_parameter("adapted").value)

        self.position = np.zeros(2, dtype=float)
        self.yaw = 0.0
        self.velocity_ref = np.zeros(2, dtype=float)
        self.nearest_obstacle = math.inf
        self.obstacle_angle = 0.0
        self.swarm: dict[int, SwarmRecord] = {}

        self.cmd_pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.best_pub = self.create_publisher(PoseStamped, "/swarm/best", 10)
        self.create_subscription(Odometry, "odom", self.odom_callback, 10)
        self.create_subscription(LaserScan, "scan", self.scan_callback, 10)
        self.create_subscription(PoseStamped, "/swarm/best", self.best_callback, 10)
        self.create_timer(self.dt, self.control_step)
        self.get_logger().info(
            f"GWO swarm controller active for robot_{self.robot_id}, target={self.target.tolist()}."
        )

    def odom_callback(self, msg: Odometry) -> None:
        self.position[:] = [msg.pose.pose.position.x, msg.pose.pose.position.y]
        self.yaw = yaw_from_quaternion(msg.pose.pose.orientation.z, msg.pose.pose.orientation.w)

    def scan_callback(self, msg: LaserScan) -> None:
        valid = [
            (index, value)
            for index, value in enumerate(msg.ranges)
            if math.isfinite(value) and msg.range_min < value < msg.range_max
        ]
        if not valid:
            self.nearest_obstacle = math.inf
            return
        index, distance = min(valid, key=lambda item: item[1])
        self.nearest_obstacle = float(distance)
        self.obstacle_angle = msg.angle_min + index * msg.angle_increment

    def best_callback(self, msg: PoseStamped) -> None:
        try:
            robot_id = int(msg.header.frame_id.replace("robot_", ""))
        except ValueError:
            return
        self.swarm[robot_id] = SwarmRecord(
            position=np.array([msg.pose.position.x, msg.pose.position.y], dtype=float),
            fitness=float(msg.pose.orientation.w),
            stamp=time.monotonic(),
        )

    def publish_fitness(self) -> None:
        fitness = float(np.linalg.norm(self.position - self.target))
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = f"robot_{self.robot_id}"
        msg.pose.position.x = float(self.position[0])
        msg.pose.position.y = float(self.position[1])
        msg.pose.orientation.w = fitness
        self.best_pub.publish(msg)
        self.swarm[self.robot_id] = SwarmRecord(self.position.copy(), fitness, time.monotonic())

    def leaders(self) -> list[np.ndarray]:
        now = time.monotonic()
        fresh_records = [record for record in self.swarm.values() if now - record.stamp < 3.0]
        if len(fresh_records) < 3:
            return [self.target, self.target, self.target]
        ranked = sorted(fresh_records, key=lambda record: record.fitness)
        return [ranked[0].position, ranked[1].position, ranked[2].position]

    def obstacle_force_world(self) -> np.ndarray:
        if not math.isfinite(self.nearest_obstacle) or self.nearest_obstacle <= 0.05:
            return np.zeros(2, dtype=float)
        if self.nearest_obstacle > 1.5:
            return np.zeros(2, dtype=float)
        obstacle_body = np.array(
            [math.cos(self.obstacle_angle), math.sin(self.obstacle_angle)], dtype=float
        )
        repulsion_body = -obstacle_body / max(self.nearest_obstacle**self.obstacle_gamma, 1e-4)
        return rotate_2d(repulsion_body, self.yaw)

    def control_step(self) -> None:
        self.publish_fitness()
        leaders = self.leaders()

        safe_u = self.u_max_nominal
        if math.isfinite(self.nearest_obstacle):
            safe_u = max(0.03, min(self.u_max_nominal, self.dvc_alpha * self.nearest_obstacle))
        c_hat = self.a_max * self.dt / math.sqrt(2.0)
        omega = max(0.0, 1.0 - (self.a_max * self.dt / max(safe_u, 1e-3)))

        acceleration = np.zeros(2, dtype=float)
        for leader in leaders:
            delta = leader - self.position
            direction = signed_unit(delta) if self.adapted else delta
            acceleration += (c_hat / 3.0) * random.random() * direction

        obstacle = self.obstacle_force_world()
        if np.linalg.norm(obstacle) > 0.0:
            acceleration += self.obstacle_gain * c_hat * random.random() * signed_unit(obstacle)

        self.velocity_ref = omega * self.velocity_ref + acceleration
        speed = float(np.linalg.norm(self.velocity_ref))
        if speed > safe_u:
            self.velocity_ref *= safe_u / speed

        body_velocity = rotate_2d(self.velocity_ref, -self.yaw)
        desired_yaw = math.atan2(self.velocity_ref[1], self.velocity_ref[0]) if speed > 1e-4 else self.yaw
        yaw_error = math.atan2(math.sin(desired_yaw - self.yaw), math.cos(desired_yaw - self.yaw))

        cmd = Twist()
        cmd.linear.x = float(np.clip(body_velocity[0], -safe_u, safe_u))
        cmd.angular.z = float(np.clip(1.8 * yaw_error + 0.4 * body_velocity[1], -1.2, 1.2))
        self.cmd_pub.publish(cmd)


def main() -> None:
    rclpy.init()
    node = SwarmRobot()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
