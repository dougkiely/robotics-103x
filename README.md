# ColumbiaX CSMM.103x Robotics

This is coursework from the Columbia University Robotics course available on edX as ColumbiaX CSMM.103x Robotics.

[Columbia University Robotics](https://www.edx.org/learn/robotics/columbia-university-robotics)

[ColumbiaX CSMM.103x](https://courses.edx.org/courses/course-v1:ColumbiaX+CSMM.103x+1T2017)

## Coursework

[Project 1](./Project_1)
Basic ROS functions to broadcast messages using ROS Publish/Subscribe features.

[Project 2](./Project_2)
ROS Transformations (tf) of a robot with a camera mounted and an object in the environment.

[Project 3](./Project_3)
Forward kinematics for a robot arm defined in a URDF file and running in a ROS environment. A forward kinematics module uses the joint values to compute the transforms from the world coordinate frame to each link of the robot.

[Project 4](./Project_4)
Cartesian controller for a 7-joint robot arm to interactively control and move the end-effector in Cartesian space, by dragging around an interactive marker. The primary goal of null-space control is to change the value of the first joint (thus turning the "elbow" of the robot) without affecting the pose of the end-effector.

[Project 5](./Project_5)
In the presence of obstacles, implement motion planning for the robot end-effector to reach a desired pose without collisions with any obstacles present in its environment, using Rapidly-exploring Random Tree (RRT) motion planner for the 7-jointed robot arm, enabling interactive maneuvering of the end-effector to the desired pose collision-free.
