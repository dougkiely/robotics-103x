#!/usr/bin/env python

from copy import deepcopy
import math
import numpy
import random
from threading import Thread, Lock
import sys

import actionlib
import control_msgs.msg
import geometry_msgs.msg
import moveit_commander
import moveit_msgs.msg
import moveit_msgs.srv
import rospy
import sensor_msgs.msg
import tf
import trajectory_msgs.msg

# [Executed at: Thu Nov 23 16:27:13 PST 2017]
#
# Python version found
# Simple Obstacle: PASSED
# Medium Obstacle: PASSED
# Hard Obstacle: PASSED

def convert_to_message(T):
    t = geometry_msgs.msg.Pose()
    position = tf.transformations.translation_from_matrix(T)
    orientation = tf.transformations.quaternion_from_matrix(T)
    t.position.x = position[0]
    t.position.y = position[1]
    t.position.z = position[2]
    t.orientation.x = orientation[0]
    t.orientation.y = orientation[1]
    t.orientation.z = orientation[2]
    t.orientation.w = orientation[3]        
    return t

def convert_from_message(msg):
    R = tf.transformations.quaternion_matrix((msg.orientation.x,
                                              msg.orientation.y,
                                              msg.orientation.z,
                                              msg.orientation.w))
    T = tf.transformations.translation_matrix((msg.position.x, 
                                               msg.position.y, 
                                               msg.position.z))
    return numpy.dot(T,R)

def convert_from_trans_message(msg):
    R = tf.transformations.quaternion_matrix((msg.rotation.x,
                                              msg.rotation.y,
                                              msg.rotation.z,
                                              msg.rotation.w))
    T = tf.transformations.translation_matrix((msg.translation.x, 
                                               msg.translation.y, 
                                               msg.translation.z))
    return numpy.dot(T,R)
   

class RRTNode(object):
    def __init__(self, parent=None, joint_points=None):
        self.parent = parent
        self.joint_points = joint_points

    # joint_points : 7-dimension vector of joint points
    def set_joint_points(self, joint_points):
        self.joint_points = joint_points

    # returns : list of 7-dimension vector of joint point values from source to goal
    def get_q_joint_values(self):
        q_list = []
        node = self
        while node.parent != None:
            q_list.append(node.joint_points)
            node = node.parent

        q_list.reverse()

        return q_list # list of q joint values

    def trim_path(self, q_sample):
        node = self
        while node.parent != None:
            if node.parent.parent == None:
                break
            v = node.joint_points # source vector v
            u = node.parent.parent.joint_points # destination vector u
            vector_projection = VectorProjection(v, u)
            descretized_path = vector_projection.descretize_path(q_sample)
            if vector_projection.is_collision_free(descretized_path):
                print("trim_path: VECTOR PROJ: COLLISION FREE")
            else:
                print("trim_path: VECTOR PROJ: COLLISION")

            node.parent = node.parent.parent
            node = node.parent


# Vector Projection
class VectorProjection(object):
    # v : v source vector
    # u : u destination vector
    # w : direction of movement vector
    # norm : magnitude/length
    # unit : unit vector
    def __init__(self, v, u):
        self.v = v
        self.u = u
        self.w = u - v
        self.norm = numpy.linalg.norm(self.w)
        self.unit = self.w/self.norm

    def find_point_at_distance(self, max_predefined_distance):
        predefined_vector = self.unit * max_predefined_distance
        return self.v + predefined_vector

    # q_simple : minimum descretization for each joint
    def descretize_path(self, q_sample):
        k = max(abs(self.unit)/numpy.array(q_sample))
        step = 1/k * self.unit
        n = 50 # 50 + 1
        return numpy.outer(numpy.arange(1, n), step) + self.v


# List of RRTNode objects
class RRTNodeList(object):

    # initialize with an empty node list
    def __init__(self, root_node=None):
        self.points = []
        if root_node != None:
            self.append(root_node)

    # append RRTNode to list of RRTNode objects
    def append(self, rrt_node):
        self.points.append(rrt_node)

    # Return the RRTNode at the specified index
    # index : RRTNode index
    # returns : the RRTNode at the specified index
    def get_node(self, index):
        if index < 0 or index > len(self.points):
            raise IndexError("Index [{}] of out bounds.".format(index))
        return self.points[index]

    # Return the number of RRTNode objects in the RRT list
    # returns: number of RRTNode objects
    def __len__(self):
        return len(self.points)

    # vector u : destination vector
    # returns : tuple(index, VectorProjection)
    def find_nearest_point(self, u):
        nearest_point = None
        for i in xrange(len(self.points)):
            v = self.points[i].joint_points # vector v (source vector)
            vector_projection = VectorProjection(v, u)

            if nearest_point == None:
                nearest_point = (i, vector_projection)
            else:
                if vector_projection.norm < nearest_point[1].norm: # norm/magnitude/length
                    nearest_point = (i, vector_projection)

        return nearest_point # index and vector projection of the nearest point


class MoveArm(object):

    def __init__(self):
        print "Motion Planning Initializing..."
        # Prepare the mutex for synchronization
        self.mutex = Lock()

        # Some info and conventions about the robot that we hard-code in here
        # min and max joint values are not read in Python urdf, so we must hard-code them here
        self.num_joints = 7
        self.q_min = []
        self.q_max = []
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        # How finely to sample each joint
        self.q_sample = [0.05, 0.05, 0.05, 0.1, 0.1, 0.1, 0.1]
        self.joint_names = ["lwr_arm_0_joint",
                            "lwr_arm_1_joint",
                            "lwr_arm_2_joint",
                            "lwr_arm_3_joint",
                            "lwr_arm_4_joint",
                            "lwr_arm_5_joint",
                            "lwr_arm_6_joint"]

        # Subscribes to information about what the current joint values are.
        rospy.Subscriber("/joint_states", sensor_msgs.msg.JointState, 
                         self.joint_states_callback)

        # Subscribe to command for motion planning goal
        rospy.Subscriber("/motion_planning_goal", geometry_msgs.msg.Transform,
                         self.move_arm_cb)

        # Publish trajectory command
        self.pub_trajectory = rospy.Publisher("/joint_trajectory", trajectory_msgs.msg.JointTrajectory, 
                                              queue_size=1)        

        # Initialize variables
        self.joint_state = sensor_msgs.msg.JointState()

        # Wait for moveit IK service
        rospy.wait_for_service("compute_ik")
        self.ik_service = rospy.ServiceProxy('compute_ik',  moveit_msgs.srv.GetPositionIK)
        print "IK service ready"

        # Wait for validity check service
        rospy.wait_for_service("check_state_validity")
        self.state_valid_service = rospy.ServiceProxy('check_state_validity',  
                                                      moveit_msgs.srv.GetStateValidity)
        print "State validity service ready"

        # Initialize MoveIt
        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()
        self.group_name = "lwr_arm"
        self.group = moveit_commander.MoveGroupCommander(self.group_name) 
        print "MoveIt! interface ready"

        # Options
        self.subsample_trajectory = True
        print "Initialization done."

    def get_joint_val(self, joint_state, name):
        if name not in joint_state.name:
            print "ERROR: joint name not found"
            return 0
        i = joint_state.name.index(name)
        return joint_state.position[i]

    def set_joint_val(self, joint_state, q, name):
        if name not in joint_state.name:
            print "ERROR: joint name not found"
        i = joint_state.name.index(name)
        joint_state.position[i] = q

    """ Given a complete joint_state data structure, this function finds the values for 
    our arm's set of joints in a particular order and returns a list q[] containing just 
    those values.
    """
    def q_from_joint_state(self, joint_state):
        q = []
        for i in range(0,self.num_joints):
            q.append(self.get_joint_val(joint_state, self.joint_names[i]))
        return q

    """ Given a list q[] of joint values and an already populated joint_state, this 
    function assumes that the passed in values are for a our arm's set of joints in 
    a particular order and edits the joint_state data structure to set the values 
    to the ones passed in.
    """
    def joint_state_from_q(self, joint_state, q):
        for i in range(0,self.num_joints):
            self.set_joint_val(joint_state, q[i], self.joint_names[i])

    """ This function will perform IK for a given transform T of the end-effector. It 
    returns a list q[] of 7 values, which are the result positions for the 7 joints of 
    the left arm, ordered from proximal to distal. If no IK solution is found, it 
    returns an empy list.
    """
    def IK(self, T_goal):
        req = moveit_msgs.srv.GetPositionIKRequest()
        req.ik_request.group_name = self.group_name
        req.ik_request.robot_state = moveit_msgs.msg.RobotState()
        req.ik_request.robot_state.joint_state = self.joint_state
        req.ik_request.avoid_collisions = True
        req.ik_request.pose_stamped = geometry_msgs.msg.PoseStamped()
        req.ik_request.pose_stamped.header.frame_id = "world_link"
        req.ik_request.pose_stamped.header.stamp = rospy.get_rostime()
        req.ik_request.pose_stamped.pose = convert_to_message(T_goal)
        req.ik_request.timeout = rospy.Duration(3.0)
        res = self.ik_service(req)
        q = []
        if res.error_code.val == res.error_code.SUCCESS:
            q = self.q_from_joint_state(res.solution.joint_state)
        return q

    """ This function checks if a set of joint angles q[] creates a valid state, or 
    one that is free of collisions. The values in q[] are assumed to be values for 
    the joints of the left arm, ordered from proximal to distal. 
    """
    def is_state_valid(self, q):
        req = moveit_msgs.srv.GetStateValidityRequest()
        req.group_name = self.group_name
        current_joint_state = deepcopy(self.joint_state)
        current_joint_state.position = list(current_joint_state.position)
        self.joint_state_from_q(current_joint_state, q)
        req.robot_state = moveit_msgs.msg.RobotState()
        req.robot_state.joint_state = current_joint_state
        res = self.state_valid_service(req)
        return res.valid

    def generate_random_point(self, q_max, q_min):
       return numpy.array(
            [(q_max[j]-q_min[j])*random.random()+q_min[j] for j in xrange(self.num_joints)])

    def find_last_valid_point(self, descretized_path):
        last_valid_point = None # last point with no collision
        for matrix_row_path_point in descretized_path:
            if self.is_state_valid(matrix_row_path_point):
                last_valid_point = matrix_row_path_point
            else:
                break
        return last_valid_point

    def is_collision_free(self, descretized_path):
        # check if there is a collision
        for matrix_row_path_point in descretized_path:
            if not self.is_state_valid(matrix_row_path_point):
                return False
        return True

    def trim_path(self, goal_rrt_node):
        while True:
            node = goal_rrt_node
            nodes_removed_count = 0
            while node.parent != None:
                if node.parent.parent == None:
                    break
                v = node.joint_points # source vector v
                u = node.parent.parent.joint_points # destination vector u
                vector_projection = VectorProjection(v, u)
                descretized_path = vector_projection.descretize_path(self.q_sample)
                if self.is_collision_free(descretized_path):
                    print("trim_path: VECTOR PROJ: COLLISION FREE")
                    node.parent = node.parent.parent
                    nodes_removed_count += 1
                else:
                    print("trim_path: VECTOR PROJ: COLLISION")

                node = node.parent

            print("trim_path: nodes removed: {}".format(nodes_removed_count))
            if nodes_removed_count == 0:
                break
        '''
        outer_node = goal_rrt_node
        while outer_node.parent != None:
            node = outer_node
            while node.parent != None:
                v = node.parent.joint_points # source vector v
                u = node.joint_points        # destination vector u
                vector_projection = VectorProjection(v, u)
                descretized_path = vector_projection.descretize_path(self.q_sample)
                if self.is_collision_free(descretized_path):
                    print("trim_path: VECTOR PROJ: COLLISION FREE")
                    outer_node.parent = node.parent
                else:
                    print("trim_path: VECTOR PROJ: COLLISION")

                node = node.parent
            outer_node = outer_node.parent
        '''

    def motion_plan(self, q_start, q_goal, q_min, q_max):
        
        # Replace this with your code

        time_started = rospy.get_time()
        timeout = time_started + 120.0
        print("-->> time started: {}, timeout: {}".format(time_started, timeout))

        #print("self.q_sample: {}".format(self.q_sample))
        #print("q_start: {}".format(q_start))
        #print("q_goal:  {}".format(q_goal))
        #print("q_min:   {}".format(q_min))
        #print("q_max:   {}".format(q_max))

        max_predefined_distance = 0.5 # delta_q = max_predefined_distance

        rrt_root_node = RRTNode(None, numpy.array(q_start))
        rrt_node_list = RRTNodeList(rrt_root_node)

        loop_count = 0
        goal_rrt_node = None
        collision_path_on_goal_count = 0
        collision_path_on_non_goal_count = 0
        while rospy.get_time() < timeout and goal_rrt_node == None:
            loop_count += 1

            # vector u (destination vector)
            u_q_rand_joint_point = self.generate_random_point(q_max, q_min)

            # vector v (source vector)
            v_nearest_point = rrt_node_list.find_nearest_point(u_q_rand_joint_point)
            parent_index = v_nearest_point[0]
            nearest_vector_projection = v_nearest_point[1]

            u_q_predefined_joint_point = nearest_vector_projection.find_point_at_distance(max_predefined_distance)

            predefined_vector_projection = VectorProjection(nearest_vector_projection.v, u_q_predefined_joint_point)
            descretized_path = predefined_vector_projection.descretize_path(self.q_sample)

            # last point with no collision
            ##last_valid_point = self.find_last_valid_point(descretized_path)
            ##
            ##if last_valid_point != None:
                ##new_rrt_node = RRTNode(rrt_node_list.get_node(parent_index), last_valid_point)
            if self.is_collision_free(descretized_path):
                new_rrt_node = RRTNode(rrt_node_list.get_node(parent_index), u_q_predefined_joint_point)
                rrt_node_list.append(new_rrt_node)

                # check that this new point connects directly to the goal point
                ##goal_vector_projection = VectorProjection(last_valid_point, q_goal)
                goal_vector_projection = VectorProjection(q_goal, u_q_predefined_joint_point)
                goal_descretized_path = goal_vector_projection.descretize_path(self.q_sample)

                if self.is_collision_free(goal_descretized_path):
                    print("COLLISION FREE to GOAL path")
                    goal_rrt_node = RRTNode(new_rrt_node, q_goal)
                    rrt_node_list.append(goal_rrt_node)
                    break
                else:
                    collision_path_on_goal_count += 1
            else:
                collision_path_on_non_goal_count += 1


            if goal_rrt_node != None:
                break

        print("final loop count: {}".format(loop_count))
        print("final RRT Node List Count: {}".format(len(rrt_node_list)))
        print("final COLLISION! path count: {}".format(collision_path_on_non_goal_count))
        print("final COLLISION! on GOAL path count: {}".format(collision_path_on_goal_count))

        q_list = []

        if goal_rrt_node:
            self.trim_path(goal_rrt_node)
            q_list = goal_rrt_node.get_q_joint_values() # list of 7-dimension joint values
            print("SUCCESS: Found Goal.")
        else:
            print("ERROR: Could not reach Goal.")

        final_time = rospy.get_time()
        elapsed_time = final_time - time_started
        print("<<-- final time: {}, timeout: {}, elapsed time: {} seconds".format(final_time, timeout, elapsed_time))

        return q_list

    def create_trajectory(self, q_list, v_list, a_list, t):
        joint_trajectory = trajectory_msgs.msg.JointTrajectory()
        for i in range(0, len(q_list)):
            point = trajectory_msgs.msg.JointTrajectoryPoint()
            point.positions = list(q_list[i])
            point.velocities = list(v_list[i])
            point.accelerations = list(a_list[i])
            point.time_from_start = rospy.Duration(t[i])
            joint_trajectory.points.append(point)
        joint_trajectory.joint_names = self.joint_names
        return joint_trajectory

    def create_trajectory(self, q_list):
        joint_trajectory = trajectory_msgs.msg.JointTrajectory()
        for i in range(0, len(q_list)):
            point = trajectory_msgs.msg.JointTrajectoryPoint()
            point.positions = list(q_list[i])
            joint_trajectory.points.append(point)
        joint_trajectory.joint_names = self.joint_names
        return joint_trajectory

    def project_plan(self, q_start, q_goal, q_min, q_max):
        q_list = self.motion_plan(q_start, q_goal, q_min, q_max)
        joint_trajectory = self.create_trajectory(q_list)
        return joint_trajectory

    def move_arm_cb(self, msg):
        T = convert_from_trans_message(msg)
        self.mutex.acquire()
        q_start = self.q_from_joint_state(self.joint_state)
        print "Solving IK"
        q_goal = self.IK(T)
        if len(q_goal)==0:
            print "IK failed, aborting"
            self.mutex.release()
            return
        print "IK solved, planning"
        trajectory = self.project_plan(numpy.array(q_start), q_goal, self.q_min, self.q_max)
        if not trajectory.points:
            print "Motion plan failed, aborting"
        else:
            print "Trajectory received with " + str(len(trajectory.points)) + " points"
            self.execute(trajectory)
        self.mutex.release()
        
    def joint_states_callback(self, joint_state):
        self.mutex.acquire()
        self.joint_state = joint_state
        self.mutex.release()

    def execute(self, joint_trajectory):
        self.pub_trajectory.publish(joint_trajectory)

if __name__ == '__main__':
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('move_arm', anonymous=True)
    ma = MoveArm()
    rospy.spin()
