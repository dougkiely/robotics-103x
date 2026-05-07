#!/usr/bin/env python  
import rospy

import numpy

import tf
import tf2_ros
import geometry_msgs.msg

# [Executed at: Mon Oct 9 16:23:27 PDT 2017]
#
# Object translation: PASSED
# Object rotation: PASSED
# Robot translation: PASSED
# Robot rotation: PASSED
# Camera translation: PASSED
# Camera aim: PASSED

def publish_transforms():
    object_transform = geometry_msgs.msg.TransformStamped()
    object_transform.header.stamp = rospy.Time.now()
    object_transform.header.frame_id = "base_frame"
    object_transform.child_frame_id = "object_frame"

    object_quaternion_tmp = tf.transformations.quaternion_from_euler(0.79, 0.0, 0.79)

    object_T = tf.transformations.concatenate_matrices(
            tf.transformations.quaternion_matrix(object_quaternion_tmp),
            tf.transformations.translation_matrix((0.0, 1.0, 1.0)))

    object_quaternion = tf.transformations.quaternion_from_matrix(object_T)
    object_transform.transform.rotation.x = object_quaternion[0]
    object_transform.transform.rotation.y = object_quaternion[1]
    object_transform.transform.rotation.z = object_quaternion[2]
    object_transform.transform.rotation.w = object_quaternion[3]

    object_translation = tf.transformations.translation_from_matrix(object_T)
    object_transform.transform.translation.x = object_translation[0]
    object_transform.transform.translation.y = object_translation[1]
    object_transform.transform.translation.z = object_translation[2]

    br.sendTransform(object_transform)

    robot_transform = geometry_msgs.msg.TransformStamped()
    robot_transform.header.stamp = rospy.Time.now()
    robot_transform.header.frame_id = "base_frame"
    robot_transform.child_frame_id = "robot_frame"
    robot_quaternion_tmp = tf.transformations.quaternion_about_axis(1.5, (0,0,1))

    robot_T = tf.transformations.concatenate_matrices(
            tf.transformations.quaternion_matrix(robot_quaternion_tmp),
            tf.transformations.translation_matrix((0.0, -1.0, 0.0)))

    robot_quaternion = tf.transformations.quaternion_from_matrix(robot_T)
    robot_transform.transform.rotation.x = robot_quaternion[0]
    robot_transform.transform.rotation.y = robot_quaternion[1]
    robot_transform.transform.rotation.z = robot_quaternion[2]
    robot_transform.transform.rotation.w = robot_quaternion[3]

    robot_translation = tf.transformations.translation_from_matrix(robot_T)
    robot_transform.transform.translation.x = robot_translation[0]
    robot_transform.transform.translation.y = robot_translation[1]
    robot_transform.transform.translation.z = robot_translation[2]

    br.sendTransform(robot_transform)
 
    camera_transform = geometry_msgs.msg.TransformStamped()
    camera_transform.header.stamp = rospy.Time.now()
    camera_transform.header.frame_id = "robot_frame"
    camera_transform.child_frame_id = "camera_frame"

    camera_T = tf.transformations.translation_matrix((0.0, 0.1, 0.1))

    camera_T_object = numpy.dot(tf.transformations.inverse_matrix(numpy.dot(robot_T, camera_T)), object_T)
    tf_vector = tf.transformations.unit_vector(tf.transformations.translation_from_matrix(camera_T_object))
    x_axis_ = [1, 0, 0]
    rotation_w_ = numpy.cross(x_axis_, tf_vector)
    angle_alpha_ = numpy.arccos(numpy.dot(x_axis_, tf_vector))

    camera_translation = tf.transformations.translation_from_matrix(camera_T)
    camera_transform.transform.translation.x = camera_translation[0]
    camera_transform.transform.translation.y = camera_translation[1]
    camera_transform.transform.translation.z = camera_translation[2]

    camera_quaternion = tf.transformations.quaternion_about_axis(angle_alpha_, rotation_w_)
    camera_transform.transform.rotation.x = camera_quaternion[0]
    camera_transform.transform.rotation.y = camera_quaternion[1]
    camera_transform.transform.rotation.z = camera_quaternion[2]
    camera_transform.transform.rotation.w = camera_quaternion[3]

    br.sendTransform(camera_transform)

if __name__ == '__main__':
    rospy.init_node('project2_solution')

    br = tf2_ros.TransformBroadcaster()
    rospy.sleep(0.5)

    while not rospy.is_shutdown():
        publish_transforms()
        rospy.sleep(0.05)
