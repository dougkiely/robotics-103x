# Project 3 FAQ

##How do run this project in my own Ubuntu machine?

        1. Launch Project 3, then in Vocareum click Actions>Download Starter code. This will download all the files you need to make the project run locally in your computer.

        2. Install the needed ROS package(s). Run the following lines on your terminal:
        ``sudo apt-get update
        sudo apt-get install ros-kinetic-urdfdom-py``

        Replace kinetic with the ROS version that you are running on your local machine.

        3. **IGNORE** all the files other than ``catkin_ws``, ``lwr_defs`` folders, and ``kuka_lwr_arm.urdf``. You should have ``lwr_defs`` folder and ``kuka_lwr_arm.urdf`` file placed in the home directory.

        4. The downloaded files are structured as a catkin workspace. You can either use this structure directly (as downloaded) and build the workspace using the "``catkin_make``" command or use whatever catkin workspace you already had, and just copy the packages inside your own src folder and run the catkin_make command. If you are having troubles with this, you should review the first ROS tutorial "Installing and configuring your ROS Environment".

        5. Once you have a catkin workspace with the packages inside the ``src`` folder, you are ready to work on your project without having to make any changes in any of the files. 

        6. NOTE: You can source both your ROS distribution and your catkin workspace automatically everytime you open up a terminal automatically by editing the ``~/.bashrc`` file in your home directory. For example if your ROS distribution is Indigo, and your catkin workspace is called "``robotics_ws``" (and is located in your home directory) then you can add the following at the end of your ``.bashrc`` file:

        ``source /opt/ros/indigo/setup.bash
        echo "ROS Indigo was sourced"
        source ~/robotics_ws/devel/setup.bash
        echo "robotics_ws workspace was sourced"``

        This way every time you open up a terminal, you will already have your workspace sourced, such that ROS will have knowledge of the packages there.

        7. *Before moving forward, if you haven't followed the instructions on step 6, you will need to source ROS and the catkin workspace every time you open a new terminal*. To run the project, first open up a terminal and type "``roscore``". In the second terminal (remember to ``source`` ROS and the catkin workspace if you didn't do step 6)  run "``rosparam set robot_description --textfile kuka_lwr_arm.urdf``", followed by "``rosrun robot_sim robot_sim_bringup``".

        8. On another 2 separate terminals you need to run the scripts for the robot mover and the your solution in forward kineamtics : "``rosrun robot_mover mover``" and "``rosrun forward_kinematics solution.py``". Note that you can find these lines from *setup_project3.sh* in the starter code.

        9. Now we can open up Rviz using "``rosrun rviz rviz``". Inside Rviz, first  change the Fixed Frame to "world_link". Then click Add and select RobotModel from the list of options. At this point if you code works, you should see the robot arm rendered and moving in a coherent way back and forth from an upright position to a another predetermined pose. You can also see the transforms if you select Add > TF. 

## I am running Ubuntu 16.04 with ROS Kinect, but ``catkin_make`` gives out an error

    To fix this, you will need to modify the file located in ``catkin_ws/src/robot_sim/CMakeLists.txt``

    ``# replace line 34``
    ``link_directories(/opt/ros/indigo/lib/)``
    ``# with``
    ``link_directories(/opt/ros/kinetic/lib/)``
