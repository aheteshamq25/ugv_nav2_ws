"""Launch Gazebo Classic with the UGV world, then spawn the robot from robot_description."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    gazebo_pkg = get_package_share_directory('ugv_gazebo')
    desc_pkg = get_package_share_directory('ugv_description')
    gazebo_ros_pkg = get_package_share_directory('gazebo_ros')

    world_file = LaunchConfiguration('world')
    xacro_file = os.path.join(desc_pkg, 'urdf', 'ugv.urdf.xacro')
    robot_description = Command(['xacro ', xacro_file])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_file, 'verbose': 'false'}.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'ugv',
                   '-x', '0.0', '-y', '0.0', '-z', '0.05'],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(gazebo_pkg, 'worlds', 'terrain_world.world'),
            description='Full path to the Gazebo world file'
        ),
        gazebo,
        robot_state_publisher,
        spawn_entity,
    ])
