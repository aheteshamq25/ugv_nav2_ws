"""Run slam_toolbox in online async mode to BUILD a map by driving the robot
around (teleop) in simulation. Save the result with:
  ros2 run nav2_map_server map_saver_cli -f ~/ugv_ws/src/ugv_navigation/maps/map
Then point ugv_navigation/maps/map.yaml (or the --map arg) at that output.
This is the closest thing to "training" Nav2 has: building/curating the map
your planner and AMCL will reason against."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'odom_frame': 'odom',
                'map_frame': 'map',
                'base_frame': 'base_footprint',
                'scan_topic': '/scan',
                'resolution': 0.05,
                'max_laser_range': 12.0,
            }]
        ),
    ])
