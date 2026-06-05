import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


INITIAL_POSES = [
    (-4.0, -2.0, 0.0),
    (-4.0, -1.2, 0.2),
    (-4.0, -0.4, -0.1),
    (-4.0, 0.4, 0.1),
    (-4.0, 1.2, -0.2),
    (-4.0, 2.0, 0.0),
]


def launch_setup(context, *args, **kwargs):
    n = int(LaunchConfiguration("n").perform(context))
    turtlebot3_gazebo = get_package_share_directory("turtlebot3_gazebo")
    model_file = os.path.join(
        turtlebot3_gazebo, "models", "turtlebot3_burger", "model.sdf"
    )
    world_file = os.path.join(turtlebot3_gazebo, "worlds", "empty_world.world")
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
        x, y, yaw = INITIAL_POSES[index % len(INITIAL_POSES)]
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
            DeclareLaunchArgument("n", default_value="6"),
            OpaqueFunction(function=launch_setup),
        ]
    )
