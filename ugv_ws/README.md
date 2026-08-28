# UGV Nav2 Workspace

A complete ROS 2 workspace for simulating and navigating a differential-drive
UGV with Nav2. Tested against **ROS 2 Humble** conventions (Gazebo Classic +
`gazebo_ros` plugins, `nav2_bringup`, `slam_toolbox`). Swap to Iron/Jazzy +
Gazebo (Ignition/Harmonic) by pointing the sim launch files at `ros_gz_sim`
instead — the Nav2 config (params, BT, launch structure) doesn't change.

## Folder structure

```
ugv_ws/
└── src/
    ├── ugv_description/      # URDF/Xacro robot model (base, wheels, lidar, IMU)
    │   ├── urdf/ugv.urdf.xacro
    │   ├── urdf/ugv.gazebo.xacro   # gazebo plugins: diff_drive, lidar, imu
    │   ├── launch/display.launch.py
    │   └── rviz/ugv.rviz
    │
    ├── ugv_gazebo/            # Simulation world + spawn
    │   ├── worlds/warehouse.world
    │   └── launch/gazebo.launch.py
    │
    ├── ugv_navigation/        # The Nav2 stack itself
    │   ├── maps/map.yaml + map.pgm      # placeholder map -- replace via SLAM
    │   ├── params/nav2_params.yaml      # AMCL, BT navigator, MPPI controller,
    │   │                                 # costmaps, planner, recovery behaviors
    │   ├── behavior_trees/navigate_w_replanning_and_recovery.xml
    │   ├── launch/localization.launch.py  # map_server + AMCL
    │   ├── launch/navigation.launch.py    # planner/controller/bt_navigator/etc
    │   ├── launch/slam.launch.py          # slam_toolbox, for building a map
    │   └── rviz/nav2_default_view.rviz
    │
    └── ugv_bringup/           # Top-level orchestration
        ├── launch/bringup_sim.launch.py   # gazebo + nav2 + rviz, one command
        ├── launch/bringup_real.launch.py  # same stack, no gazebo, real driver
        └── config/ekf.yaml                # optional wheel+IMU sensor fusion
```

## Prerequisites (Ubuntu 22.04 + ROS 2 Humble)

```bash
sudo apt install ros-humble-desktop ros-humble-navigation2 ros-humble-nav2-bringup \
  ros-humble-gazebo-ros-pkgs ros-humble-slam-toolbox ros-humble-robot-localization \
  ros-humble-xacro ros-humble-joint-state-publisher-gui
```

## Build

```bash
cd ugv_ws
colcon build --symlink-install
source install/setup.bash
```

## 1. Sanity-check the robot model (no sim)

```bash
ros2 launch ugv_description display.launch.py
```

## 2. Build a real map (first time only)

The placeholder `map.pgm` is a blank grid so the workspace runs immediately —
replace it with a real map before trusting navigation.

```bash
# Terminal 1: sim + SLAM
ros2 launch ugv_gazebo gazebo.launch.py
ros2 launch ugv_navigation slam.launch.py

# Terminal 2: drive the robot around to build the map
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Terminal 3: once the map looks complete, save it
ros2 run nav2_map_server map_saver_cli -f src/ugv_navigation/maps/map
```

## 3. Full simulation with navigation

```bash
ros2 launch ugv_bringup bringup_sim.launch.py
```

This starts Gazebo, spawns the robot, brings up AMCL + the map, starts the
full Nav2 stack (planner, MPPI controller, costmaps, recoveries, BT
navigator), and opens RViz with the Nav2 panel. In RViz:
1. Click **2D Pose Estimate**, set the robot's actual starting pose.
2. Click **Nav2 Goal**, click a point on the map — the robot plans and drives there.

## 4. Real robot

```bash
ros2 launch ugv_bringup bringup_real.launch.py map:=/path/to/your_map.yaml
```

Requires your robot's driver node publishing `/scan`, `/odom`, and TF
`odom -> base_footprint` (or fuse wheel+IMU odometry first via
`ugv_bringup/config/ekf.yaml` + `robot_localization`'s `ekf_node`).

## "Training" the robot — what to actually tune

Nav2 has no ML model to train; the equivalent workflow is tuning the YAML
plugin config in `nav2_params.yaml` against your UGV's real kinematics and
environment:

| Symptom | What to tune |
|---|---|
| Robot clips corners / drives too close to obstacles | `inflation_layer.inflation_radius`, `cost_scaling_factor` in both costmaps |
| Robot too slow / too cautious | `FollowPath.vx_max`, `ax_max`, `velocity_smoother.max_velocity` |
| Robot oscillates or jitters near goal | `general_goal_checker.xy_goal_tolerance`, `PathAlignCritic`/`GoalCritic` weights |
| Robot gets stuck often | `behavior_server` recovery params, add/reorder actions in the BT XML |
| Localization drifts or jumps | `amcl.max_particles`, `alphaN` odometry noise params, or fuse an IMU via `ekf.yaml` |
| Planner picks bad routes through tight spaces | `planner_server.GridBased.tolerance`, `robot_radius`, consider `nav2_smac_planner` for non-circular footprints |

Iterate in simulation (`bringup_sim.launch.py`) before touching the real
robot — Gazebo gives you the same `/scan`, `/odom`, and TF tree Nav2 expects,
so no navigation config should need to change between sim and real beyond
`use_sim_time`.

## Real robot base footprint / Ackermann steering

This model assumes differential drive. For a skid-steer or Ackermann UGV,
swap `libgazebo_ros_diff_drive.so` in `ugv.gazebo.xacro` for the matching
plugin, set `FollowPath.motion_model` to `"Ackermann"` (with `min_turning_r`)
in `nav2_params.yaml`, and consider `nav2_smac_planner` (Hybrid-A*) instead of
NavFn for the global planner, since it respects non-holonomic constraints.
