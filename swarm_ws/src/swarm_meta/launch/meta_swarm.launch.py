import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


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
    actions = [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(turtlebot3_gazebo, "launch", "empty_world.launch.py")
            )
        )
    ]
    for index in range(n):
        x, y, yaw = INITIAL_POSES[index % len(INITIAL_POSES)]
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
            DeclareLaunchArgument("n", default_value="6"),
            OpaqueFunction(function=launch_setup),
        ]
    )
