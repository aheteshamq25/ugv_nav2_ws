"""ONE-SHOT SIMULATION LAUNCH.
Brings up: Gazebo + UGV spawn -> localization (map_server+AMCL) -> full Nav2
stack -> RViz with the Nav2 panel. Equivalent of "start everything and drive".

Usage:
  ros2 launch ugv_bringup bringup_sim.launch.py
  ros2 launch ugv_bringup bringup_sim.launch.py map:=/path/to/your_map.yaml
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    gazebo_pkg = get_package_share_directory('ugv_gazebo')
    nav_pkg = get_package_share_directory('ugv_navigation')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg, 'launch', 'gazebo.launch.py')
        )
    )

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_pkg, 'launch', 'localization.launch.py')
        ),
        launch_arguments={'map': map_yaml, 'params_file': params_file,
                           'use_sim_time': use_sim_time}.items()
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_pkg, 'launch', 'navigation.launch.py')
        ),
        launch_arguments={'params_file': params_file,
                           'use_sim_time': use_sim_time}.items()
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(nav_pkg, 'rviz', 'nav2_default_view.rviz')],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=None
    )

    # Give Gazebo a couple seconds to come up and publish TF/robot_description
    # before starting localization + navigation stacks.
    delayed_localization = TimerAction(period=5.0, actions=[localization])
    delayed_navigation = TimerAction(period=7.0, actions=[navigation])
    delayed_rviz = TimerAction(period=7.0, actions=[rviz])

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=os.path.join(nav_pkg, 'maps', 'map.yaml')),
        DeclareLaunchArgument('params_file', default_value=os.path.join(nav_pkg, 'params', 'nav2_params.yaml')),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),

        gazebo,
        delayed_localization,
        delayed_navigation,
        delayed_rviz,
    ])
