#!/usr/bin/env python
# A very basic TurtleBot script that moves TurtleBot forward indefinitely. Press CTRL + C to stop.  To run:
# On TurtleBot:
# roslaunch turtlebot_bringup minimal.launch
# On work station:
# python move.py

import rospy
from gazebo_msgs.msg import ModelStates
from nav_msgs.msg import Odometry 
import math
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import Point, Twist
from math import atan2

class Move_path:

    def forward(self,x,y,w):
        # rospy.loginfo("Moving - lin : {} ang : {}".format(lin,ang))
        # Twist is a datatype for velocity
        move_cmd = Twist()
	    # let's go forward 
        move_cmd.linear.x = x
        move_cmd.linear.y = y
	    # let's turns
        move_cmd.angular.z = w
	    # publish the velocity
        self.pub.publish(move_cmd)

    def pose_callback(self, msg):
        self.x = msg.pose[2].position.x
        self.y = msg.pose[2].position.y
        self.z = msg.pose[2].position.z

        #we obtain angles in quaternion format
        self.xt = msg.pose[2].orientation.x
        self.yt = msg.pose[2].orientation.y
        self.zt = msg.pose[2].orientation.z
        self.wt = msg.pose[2].orientation.w
        rospy.loginfo("Position: %f,%f,%f",self.x,self.y,self.z)


    #Go to a goal taking care of obstale avoidance(using states obtained) given the x coordinate
    def go_to_goal(self, goal_x, goal_y):

        speed = Twist()
        r = rospy.Rate(10)
        goal = Point()
        goal.x =  goal_x
        goal.y = goal_y
        

        while not rospy.is_shutdown():

            inc_x = goal.x -self.odom_x
            inc_y = goal.y -self.odom_y
            angle_to_goal = atan2(inc_y, inc_x)

                
            if abs(angle_to_goal - self.odom_theta) > 0.5:
                speed.linear.x = 0.0
                speed.angular.z = 0.3
            elif abs(angle_to_goal - self.odom_theta) > 0.2:
                speed.linear.x = 0.0
                speed.angular.z = 0.1
            else:
                speed.linear.x = 0.5
                speed.angular.z = 0.0

            if (abs(inc_x)<0.05 and abs(inc_y)<0.05):
                break

            self.pub.publish(speed)
            r.sleep()    


    def __init__(self):
        rospy.init_node('GoForward', anonymous=False)
        rospy.loginfo("To stop TurtleBot CTRL + C")  
        rospy.on_shutdown(self.shutdown)

        rospy.Subscriber("/gazebo/model_states", ModelStates, self.pose_callback)
        self.sub2 = rospy.Subscriber("/odom", Odometry, self.odometry) 
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        self.odom_x = 0
        self.odom_y = 0
        self.odom_theta =0
        self.state= 0
        self.invert =1
        self.linear_vel = 0
        self.iter_state1 =0
     
        r = rospy.Rate(10)
        self.x =9
        self.y =0
        self.z =0
        self.xt=0
        self.yt=0
        self.zt=0
        self.wt=0
	

        while not rospy.is_shutdown():
            # t0 = rospy.get_rostime().secs
            n = 0
            N = 1000
            while(self.odom_x < (9+3*math.pi)):

                goal_x = ((3*math.pi*(n+1))/N) 
                goal_y = math.sin(2*goal_x)*math.sin(goal_x/2)*math.exp(-0.01)
                goal_x+= math.pi*3
                self.go_to_goal(goal_x, goal_y)
                n+=1


            
        self.shutdown()
        # break

    
    def odometry(self, msg): # callback function for odometry
        self.odom_x = msg.pose.pose.position.x
        self.odom_y = msg.pose.pose.position.y
        rot_q = msg.pose.pose.orientation
        (roll, pitch, theta) = euler_from_quaternion([rot_q.x, rot_q.y, rot_q.z, rot_q.w])
        self.odom_theta = theta    
        
    def shutdown(self):
        rospy.loginfo("Stop TurtleBot")
        self.pub.publish(Twist())
        rospy.sleep(1)
 
if __name__ == '__main__':
    move = Move_path()
    # try:
    #     move = Move_path()
    # except:
    #     rospy.loginfo("GoForward node terminated.")