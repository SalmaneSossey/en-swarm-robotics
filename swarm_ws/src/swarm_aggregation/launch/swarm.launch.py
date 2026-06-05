import os
import random

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def launch_setup(context, *args, **kwargs):
    n = int(LaunchConfiguration("n").perform(context))
    arena = float(LaunchConfiguration("arena").perform(context))
    seed = int(LaunchConfiguration("seed").perform(context))
    random.seed(seed)

    turtlebot3_gazebo = get_package_share_directory("turtlebot3_gazebo")
    swarm_aggregation = get_package_share_directory("swarm_aggregation")
    model_file = os.path.join(
        turtlebot3_gazebo, "models", "turtlebot3_burger", "model.sdf"
    )
    world_file = os.path.join(swarm_aggregation, "worlds", "aggregation_arena.world")
    actions = [
        ExecuteProcess(
            cmd=[
                "gzserver",
                "-s",
                "libgazebo_ros_init.so",
                "-s",
                "libgazebo_ros_factory.so",
                world_file,
            ],
            output="screen",
        ),
        ExecuteProcess(
            cmd=["gzclient"],
            output="screen",
        ),
    ]

    for index in range(n):
        x = random.uniform(-arena, arena)
        y = random.uniform(-arena, arena)
        yaw = random.uniform(0.0, 6.283185307)
        actions.append(
            ExecuteProcess(
                cmd=[
                    "/usr/bin/python3",
                    "/opt/ros/humble/lib/gazebo_ros/spawn_entity.py",
                    "-entity",
                    f"robot_{index}",
                    "-file",
                    model_file,
                    "-x",
                    f"{x:.3f}",
                    "-y",
                    f"{y:.3f}",
                    "-Y",
                    f"{yaw:.3f}",
                    "-robot_namespace",
                    f"/robot_{index}",
                ],
                output="screen",
            )
        )
    return actions


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("n", default_value="10"),
            DeclareLaunchArgument("arena", default_value="4.0"),
            DeclareLaunchArgument("seed", default_value="7"),
            OpaqueFunction(function=launch_setup),
        ]
    )
