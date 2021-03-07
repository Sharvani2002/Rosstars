#!/usr/bin/env python
# A very basic TurtleBot script that moves TurtleBot forward indefinitely. Press CTRL + C to stop.  To run:
# On TurtleBot:
# roslaunch turtlebot_bringup minimal.launch
# On work station:
# python move.py

import rospy
from geometry_msgs.msg import Twist
from gazebo_msgs.msg import ModelStates
import math

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
        self.cmd_vel.publish(move_cmd)

    def pose_callback(self, msg):
        self.x = msg.pose[2].position.x
        self.y = msg.pose[2].position.y
        self.z = msg.pose[2].position.z
        rospy.loginfo("Position: %f,%f,%f",self.x,self.y,self.z)


    def __init__(self):
        # initiliaze
        rospy.init_node('GoForward', anonymous=False)

	    # tell user how to stop TurtleBot
        rospy.loginfo("To stop TurtleBot CTRL + C")

        # What function to call when you ctrl + c    
        rospy.on_shutdown(self.shutdown)

        rospy.Subscriber("/gazebo/model_states", ModelStates, self.pose_callback)
        
	    # Create a publisher which can "talk" to TurtleBot and tell it to move
        # Tip: You may need to change cmd_vel_mux/input/navi to /cmd_vel if you're not using TurtleBot2
        self.cmd_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
     
	    #TurtleBot will stop if we don't keep telling it to move.  How often should we tell it to move? 10 HZ
        r = rospy.Rate(10)
        self.x =9
        self.y =0
        self.z =0 
	

        while not rospy.is_shutdown():
            # # Move forward at 1 for 1 sec
            t0 = rospy.get_rostime().secs

            ########################################
            #Change the code from here


            #distance in x direction
            dist_x =6 ##calculate desired total distance in x direction

            # while(t0 + 300 >= rospy.get_rostime().secs):

            #9 is the original or initial position
            while(abs(self.x-9) <= dist_x):
                
                x = 0.1
                w = 0
                y = (2*math.cos(2*(self.x-9))*math.sin((self.x-9)/2) + 0.5*math.sin(2*(self.x-9))*math.cos((self.x-9)/2))
                # y =0

                self.forward(x,y,w)
                #One sol to the riddle: a=2,b=0,c=1

                #sin(x*2)*sin(x/2)

                #Update the velocities accordingly...
                # x = 1#update x
                # y = 1#update y
                
                # w = 1#update angular vel

            
            #########################################
            break
        self.shutdown()
        # break
                            
        
    def shutdown(self):
        # stop turtlebot
        rospy.loginfo("Stop TurtleBot")
	    # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop TurtleBot
        self.cmd_vel.publish(Twist())
	    # sleep just makes sure TurtleBot receives the stop command prior to shutting down the script
        rospy.sleep(1)
 
if __name__ == '__main__':
    try:
        move = Move_path()
	
    except:
        rospy.loginfo("GoForward node terminated.")
