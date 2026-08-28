#!/usr/bin/env python3
"""
Send a sequence of navigation goals to Nav2 programmatically using
nav2_simple_commander, instead of clicking 'Nav2 Goal' in RViz each time.

The robot drives through each waypoint in order, using the same
planner/controller/obstacle-avoidance stack as an RViz-clicked goal --
this script is just a different way of triggering it.

Usage:
    source ~/ugv_nav2_ws/ugv_ws/install/setup.bash
    python3 ~/ugv_nav2_ws/ugv_ws/src/ugv_navigation/scripts/patrol.py

Requires bringup_sim.launch.py (or bringup_real.launch.py) already running
in another terminal, with localization active.
"""

import sys
import rclpy
from rclpy.duration import Duration
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


def make_pose(navigator, x, y, yaw_deg):
    """Build a PoseStamped in the map frame from x, y, and a yaw in degrees."""
    import math
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    yaw = math.radians(yaw_deg)
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def main():
    rclpy.init()
    navigator = BasicNavigator()

    # ------------------------------------------------------------------
    # 1. Set the robot's starting pose (skip this block if you already
    #    set it via '2D Pose Estimate' in RViz -- don't do both).
    # ------------------------------------------------------------------
    initial_pose = make_pose(navigator, x=0.0, y=0.0, yaw_deg=0.0)
    navigator.setInitialPose(initial_pose)

    # Wait for Nav2 (planner, controller, bt_navigator, etc.) to be active.
    navigator.waitUntilNav2Active()

    # ------------------------------------------------------------------
    # 2. Define your waypoints here: (x, y, yaw_degrees) in the map frame.
    #    Edit these to match real open space in your map.
    # ------------------------------------------------------------------
    waypoints = [
        make_pose(navigator, x=1.5, y=0.0, yaw_deg=0.0),
        make_pose(navigator, x=1.5, y=1.5, yaw_deg=90.0),
        make_pose(navigator, x=0.0, y=1.5, yaw_deg=180.0),
        make_pose(navigator, x=0.0, y=0.0, yaw_deg=-90.0),
    ]

    # ------------------------------------------------------------------
    # 3. Drive through all waypoints in sequence. followWaypoints() drives
    #    to each one individually (stops briefly at each); goThroughPoses()
    #    treats them as an intermediate path and doesn't fully stop at each.
    #    followWaypoints is easier to reason about when starting out.
    # ------------------------------------------------------------------
    navigator.followWaypoints(waypoints)

    i = 0
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        i += 1
        if feedback and i % 10 == 0:
            print(f'Currently heading to waypoint {feedback.current_waypoint + 1}'
                  f' of {len(waypoints)}')

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('Patrol complete -- all waypoints reached.')
    elif result == TaskResult.CANCELED:
        print('Patrol was canceled.')
    elif result == TaskResult.FAILED:
        print('Patrol failed -- check terminal running bringup_sim.launch.py for the cause.')
    else:
        print('Patrol finished with an unknown result.')

    navigator.lifecycleShutdown()
    rclpy.shutdown()


if __name__ == '__main__':
    main()