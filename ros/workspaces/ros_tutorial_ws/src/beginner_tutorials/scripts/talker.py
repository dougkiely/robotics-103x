#!/usr/bin/env python
# Every Python ROS Node will have this declaration at the top.
# The first line makes sure your script is executed as a Python script.
# license removed for brevity
# import rospy required if writing a Python ROS Node
import rospy

# from std_msgs.mgs import String to reuse the std_msgs/String message type (a simple string container) for publishing
from std_msgs.msg import String

# This code defines the talker's interface to the rest of ROS.
def talker():

  # declare that your node is publishing to the chatter topic using the
  # message type String. String here is actually the class std_msgs.msg.String. 
  # The queue_size argument is New in ROS hydro and limits the amount of queued
  # messages if any subscriber is not receiving the them fast enough. In older
  # ROS distributions just omit the argument.
  pub = rospy.Publisher('chatter', String, queue_size=10)

  # The next line, rospy.init_node(NAME), is very important as it tells rospy
  # the name of your node -- until rospy has this information, it cannot start
  # communicating with the ROS Master. In this case, your node will take on the
  # name talker. Note: the name must be a base name, i.e. it cannot contain any
  # slashes "/".
  rospy.init_node('talker', anonymous=True)

  # This line creates a Rate object rate. With the help of its method sleep(),
  # it offers a convenient way for looping at the desired rate. With its
  # argument of 10, we should expect to go through the loop 10 times per second
  # (as long as our processing time does not exceed 1/10th of a second!)
  rate = rospy.Rate(10) # 10hz

  # This loop is a fairly standard rospy construct: checking the
  # rospy.is_shutdown() flag and then doing work. You have to
  # check is_shutdown() to check if your program should exit (e.g.
  # if there is a Ctrl-C or otherwise). In this case, the "work" is
  # a call to pub.publish(hello_str) that publishes a string to our
  # chatter topic. The loop calls r.sleep(), which sleeps just long
  # enough to maintain the desired rate through the loop.
  #
  # (You may also run across rospy.sleep() which is similar to
  # time.sleep() except that it works with simulated time as well (see Clock).)
  #
  # This loop also calls rospy.loginfo(str), which performs triple-duty:
  # the messages get printed to screen, it gets written to the Node's log file,
  # and it gets written to rosout. rosout is a handy for debugging: you can
  # pull up messages using rqt_console instead of having to find the console
  # window with your Node's output. 
  #
  # std_msgs.msg.String is a very simple message type, so you may be wondering
  # what it looks like to publish more complicated types. The general rule of
  # thumb is that constructor args are in the same order as in the .msg file.
  # You can also pass in no arguments and initialize the fields directly, e.g.
  #
  #  msg = String()
  #  msg.data = str
  #
  # or you can initialize some of the fields and leave the rest with default
  # values:
  #
  #  String(data=str)
  #
  while not rospy.is_shutdown():
    hello_str = "hello world %s" % rospy.get_time()
    rospy.loginfo(hello_str)
    pub.publish(hello_str)
    rate.sleep()

# In addition to the standard Python __main__ check, this catches a
# rospy.ROSInterruptException exception, which can be thrown by rospy.sleep()
# and rospy.Rate.sleep() methods when Ctrl-C is pressed or your Node is
# otherwise shutdown. The reason this exception is raised is so that you don't
# accidentally continue executing code after the sleep().
if __name__ == '__main__':
  try:
    talker()
  except rospy.ROSInterruptException:
    pass
