import math
import random
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

V_LIN = 0.12
V_ANG = 0.80
D_MIN = 1.00
T_STOP = 8.0
CONTROL_PERIOD = 0.10


class AggregationRobot(Node):
    def __init__(self) -> None:
        super().__init__("aggregation_robot")
        self.cmd_pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.create_subscription(LaserScan, "scan", self.scan_callback, 10)
        self.state = "MOVING"
        self.neighbor_close = False
        self.neighbor_density = 0.0
        self.stop_until = 0.0
        self.turn_until = 0.0
        self.turn_speed = 0.0
        self.wander_until = 0.0
        self.wander_speed = 0.0
        self.create_timer(CONTROL_PERIOD, self.loop)
        self.get_logger().info(f"BEECLUST controller active in namespace {self.get_namespace()}.")

    def scan_callback(self, msg: LaserScan) -> None:
        valid_ranges = [
            value
            for value in msg.ranges
            if math.isfinite(value) and msg.range_min < value < msg.range_max
        ]
        self.neighbor_close = bool(valid_ranges) and min(valid_ranges) < D_MIN
        close_ranges = [value for value in valid_ranges if value < D_MIN]
        self.neighbor_density = len(close_ranges) / max(len(valid_ranges), 1)

    def loop(self) -> None:
        cmd = Twist()
        now = time.monotonic()

        if self.state == "MOVING":
            cmd.linear.x = V_LIN
            if now >= self.wander_until:
                self.wander_speed = random.uniform(-0.25, 0.25)
                self.wander_until = now + random.uniform(2.0, 5.0)
            cmd.angular.z = self.wander_speed
            if self.neighbor_close:
                self.state = "STOPPED"
                density_bonus = min(6.0, 40.0 * self.neighbor_density)
                self.stop_until = now + T_STOP + density_bonus
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0

        elif self.state == "STOPPED":
            if now >= self.stop_until:
                angle = random.uniform(math.pi / 2.0, 2.0 * math.pi)
                self.turn_speed = random.choice([-1.0, 1.0]) * V_ANG
                self.turn_until = now + angle / V_ANG
                self.state = "TURNING"

        elif self.state == "TURNING":
            cmd.angular.z = self.turn_speed
            if now >= self.turn_until:
                self.state = "MOVING"
                cmd.angular.z = 0.0
                self.wander_until = 0.0

        self.cmd_pub.publish(cmd)


def main() -> None:
    rclpy.init()
    node = AggregationRobot()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
