"""REAL-ROBOT LAUNCH.
Same stack as bringup_sim.launch.py but without Gazebo: assumes your robot's
driver node is already publishing /scan, /odom (or an EKF-fused /odom, see
config/ekf.yaml), and TF odom->base_footprint. Starts robot_state_publisher
from the real URDF, localization, and navigation with use_sim_time:=false.

Usage:
  ros2 launch ugv_bringup bringup_real.launch.py map:=/path/to/your_map.yaml
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node


def generate_launch_description():
    desc_pkg = get_package_share_directory('ugv_description')
    nav_pkg = get_package_share_directory('ugv_navigation')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')

    xacro_file = os.path.join(desc_pkg, 'urdf', 'ugv.urdf.xacro')
    robot_description = Command(['xacro ', xacro_file])

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': False}]
    )

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_pkg, 'launch', 'localization.launch.py')
        ),
        launch_arguments={'map': map_yaml, 'params_file': params_file,
                           'use_sim_time': 'false'}.items()
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_pkg, 'launch', 'navigation.launch.py')
        ),
        launch_arguments={'params_file': params_file, 'use_sim_time': 'false'}.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=os.path.join(nav_pkg, 'maps', 'map.yaml')),
        DeclareLaunchArgument('params_file', default_value=os.path.join(nav_pkg, 'params', 'nav2_params.yaml')),

        robot_state_publisher,
        localization,
        navigation,
    ])
