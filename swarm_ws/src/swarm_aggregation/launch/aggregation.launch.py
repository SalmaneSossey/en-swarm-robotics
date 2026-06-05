from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    n = int(LaunchConfiguration("n").perform(context))
    return [
        Node(
            package="swarm_aggregation",
            executable="aggregation_robot",
            namespace=f"robot_{index}",
            output="screen",
        )
        for index in range(n)
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("n", default_value="10"),
            OpaqueFunction(function=launch_setup),
        ]
    )
