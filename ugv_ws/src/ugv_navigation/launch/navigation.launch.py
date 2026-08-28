"""Launch the Nav2 stack (planner, controller, behaviors, bt_navigator, velocity_smoother,
waypoint_follower) via nav2_bringup's bringup_launch.py, pointed at this package's
params and behavior tree. Assumes localization (AMCL) is already running --
see localization.launch.py, or bringup_sim.launch.py in ugv_bringup which chains both."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    nav_pkg = get_package_share_directory('ugv_navigation')
    nav2_bringup_pkg = get_package_share_directory('nav2_bringup')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_pkg, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'params_file': params_file,
            'use_sim_time': use_sim_time,
            'autostart': autostart,
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument('params_file', default_value=os.path.join(nav_pkg, 'params', 'nav2_params.yaml')),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart', default_value='true'),
        nav2_bringup_launch,
    ])
