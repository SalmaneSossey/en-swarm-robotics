import os
import random

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    n = int(LaunchConfiguration("n").perform(context))
    arena = float(LaunchConfiguration("arena").perform(context))
    seed = int(LaunchConfiguration("seed").perform(context))
    random.seed(seed)

    turtlebot3_gazebo = get_package_share_directory("turtlebot3_gazebo")
    model_file = os.path.join(
        turtlebot3_gazebo, "models", "turtlebot3_burger", "model.sdf"
    )
    actions = [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(turtlebot3_gazebo, "launch", "empty_world.launch.py")
            )
        )
    ]

    for index in range(n):
        x = random.uniform(-arena, arena)
        y = random.uniform(-arena, arena)
        yaw = random.uniform(0.0, 6.283185307)
        actions.append(
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=[
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
