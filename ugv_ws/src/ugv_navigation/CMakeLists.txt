cmake_minimum_required(VERSION 3.8)
project(ugv_navigation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY maps params behavior_trees launch rviz
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/patrol.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
