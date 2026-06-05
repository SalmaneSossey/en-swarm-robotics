from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    n = int(LaunchConfiguration("n").perform(context))
    algorithm = LaunchConfiguration("algorithm").perform(context).lower()
    adapted = LaunchConfiguration("adapted").perform(context).lower()
    if algorithm != "gwo":
        raise RuntimeError("This TP6 implementation currently supports algorithm:=gwo.")
    return [
        Node(
            package="swarm_meta",
            executable="swarm_robot",
            namespace=f"robot_{index}",
            output="screen",
            parameters=[{"robot_id": index, "n": n, "adapted": adapted == "true"}],
        )
        for index in range(n)
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("n", default_value="6"),
            DeclareLaunchArgument("algorithm", default_value="gwo"),
            DeclareLaunchArgument("adapted", default_value="true"),
            OpaqueFunction(function=launch_setup),
        ]
    )
