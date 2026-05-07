#!/usr/bin/env python
import rospy
from std_msgs.msg import String

# callback-based mechanism for subscribing to messages
# callback is invoked with the message as the first argument
def callback(data):
  rospy.loginfo(rospy.get_caller_id() + " I heard %s", data.data)

# This code defines the listener's interface to the rest of ROS.
def listener():

  # In ROS, nodes are uniquely named. If two nodes with the same
  # node are launched, the previous one is kicked off. The
  # anonymous=True flag means that rospy will choose a unique
  # name for our 'listener' node so that multiple listeners can
  # run simultaneously.
  # We also changed up the call to rospy.init_node() somewhat. We've
  # added the anonymous=True keyword argument. ROS requires that each
  # node have a unique name. If a node with the same name comes up, it
  # bumps the previous one. This is so that malfunctioning nodes can
  # easily be kicked off the network. The anonymous=True flag tells
  # rospy to generate a unique name for the node so that you can have
  # multiple listener.py nodes run easily.
  rospy.init_node('listener', anonymous=True)

  # This declares that your node subscribes to the chatter topic which is
  # of type std_msgs.msgs.String. When new messages are received, callback
  # is invoked with the message as the first argument. 
  rospy.Subscriber("chatter", String, callback)

  # spin() simply keeps python from exiting until this node is stopped
  # The final addition, rospy.spin() simply keeps your node from exiting until
  # the node has been shutdown. Unlike roscpp, rospy.spin() does not affect
  # the subscriber callback functions, as those have their own threads.
  rospy.spin()

if __name__ == '__main__':
  listener()
