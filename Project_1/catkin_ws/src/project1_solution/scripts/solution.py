#!/usr/bin/env python  
import rospy

from std_msgs.msg import Int16
from project1_solution.msg import TwoInts

class SumInts:

  def run(self):
    rospy.init_node('summer', anonymous=True)
    self.init_publisher()
    self.listener_node()

  def init_publisher(self):
    self.pub = rospy.Publisher('sum', Int16, queue_size=100)

  def listener_node(self):
    rospy.Subscriber('two_ints', TwoInts, self.subscriber_callback)
    rospy.spin()

  def subscriber_callback(self, X):
    self.pub.publish(X.a + X.b)

if __name__ == '__main__':
  SumInts().run()
