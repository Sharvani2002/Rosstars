#!/usr/bin/env python
import rospy # Python library for ROS
from sensor_msgs.msg import LaserScan #import library for lidar sensor
from nav_msgs.msg import Odometry #import library for position and orientation data
# from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import Point, Twist
from math import atan2
from gazebo_msgs.msg import ModelStates


class Moving(): 
    def __init__(self): 
        # global circle
        # circle = Twist() 
        self.pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10) 
        self.sub1 = rospy.Subscriber("/scan", LaserScan, self.callback) 
        self.sub2 = rospy.Subscriber("/odom", Odometry, self.odometry) 


        self.odom_x = 0
        self.odom_y = 0
        self.odom_theta =0
        self.state= 0
        self.invert =1
        self.linear_vel = 0
        self.iter_state1 =0

    def callback(self, msg): #function for obstacle avoidance
        print '-------RECEIVING LIDAR SENSOR DATA-------'
        print 'Front: {}'.format(msg.ranges[0]) #lidar data for front side
        print 'Left:  {}'.format(msg.ranges[90]) #lidar data for left side
        print 'Right: {}'.format(msg.ranges[270]) #lidar data for right side
        print 'Back: {}'.format(msg.ranges[180]) #lidar data for back side

        global regions
        regions = {
            'bright':  min(min(msg.ranges[0:71]), 2),
            'fright': min(min(msg.ranges[72:143]), 2),
            'front':  min(min(msg.ranges[144:215]), 2),
            'fleft':  min(min(msg.ranges[216:287]), 2),
            'bleft':   min(min(msg.ranges[288:359]), 2),
        }

        # wall_state_check()
        # this is a way to handle laser call back, here msg has 720, but remember our bot has 360, you could also add extra functions
        #  with a call so that it can get updated continuously
        #Go to a goal taking care of obstale avoidance(using states obtained) given the x coordinate
        
      	#Obstacle Avoidance distance
        self.distance = 0.05
        '''
        Updates states as follows:
        0: if everything is fine
        1: if it detects obstacle within self.distance range
        2: if it detects no obtacle after detecting an obstacle previously(in same loop)
        '''    

        if msg.ranges[0] > 0.5 and msg.ranges[15] > 0.5 and msg.ranges[345] > 0.5: 
            #when no any obstacle near detected even far away
            self.state = 10#very safe
        
        if msg.ranges[0] > 3 and msg.ranges[15] > 3 and msg.ranges[345] > 3: 
            #when no any obstacle near detected even faaaar away
            self.state = 100#extremely safe

        elif (msg.ranges[0] <= self.distance and msg.ranges[15] <= self.distance and msg.ranges[345] <= self.distance):
            rospy.loginfo("An Obstacle Near Detected")
            self.state = 1
            self.iter_state1+=1

            if msg.ranges[0] > self.distance and msg.ranges[15] > self.distance and msg.ranges[345] > self.distance and msg.ranges[45] > self.distance and msg.ranges[315] > self.distance:
                #when no any obstacle near detected after rotation
                self.state= 2

        else:
            self.state =0 
    

 




    def go_to_goal(self, given_x):

        speed = Twist()
        r = rospy.Rate(10)
        goal = Point()
        goal.x = given_x
        goal.y = 0

        while not rospy.is_shutdown():

            inc_x = goal.x -self.odom_x
            inc_y = goal.y -self.odom_y
            angle_to_goal = atan2(inc_y, inc_x)

            if (self.state==0 or self.state==2):
                
                if abs(angle_to_goal - self.odom_theta) > 0.1:
                    speed.linear.x = 0.0
                    speed.angular.z = 0.3
                else:
                    speed.linear.x = 0.5
                    speed.angular.z = 0.0
            #move a bit faster
            if (self.state ==10):
                if abs(angle_to_goal - self.odom_theta) > 0.1:
                    speed.linear.x = 0.0
                    speed.angular.z = 0.3
                else:
                    speed.linear.x = 0.8
                    speed.angular.z = 0.0
            #move very fast
            if (self.state ==100):
                if abs(angle_to_goal - self.odom_theta) > 0.1:
                    speed.linear.x = 0.0
                    speed.angular.z = 0.3
                else:
                    speed.linear.x = 1
                    speed.angular.z = 0.0

            
            if (self.state==1 and self.iter_state1 < 10):
                # self.invert = -self.invert
                # speed.angular.z = 0.5*self.invert
                if abs(angle_to_goal - self.odom_theta) > 0.5:
                    speed.angular.z = 0.3
                else:
                    speed.angular.z = 0.1

                speed.linear.x = 0
                speed.linear.y = 0

            #if after rotating many times it is not able to 
            #move in an angle directed to the goal
            #Thne move in the direction where there is less obstacle
            if(self.state==1 and self.iter_state1 >= 10):
                speed.angular.z = 0.1
                speed.linear.x = 0
                speed.linear.y = 0

                if (self.state==0 or self.state ==10 or self.state ==100):
                    speed.linear.x = 0.2
                    self.iter_state1 = 0


            #Stop when the goal is reached
            if (abs(inc_x)<0.5 and abs(inc_y)<0.5):
                break

            self.pub.publish(speed)
            r.sleep()    



    def odometry(self, msg): # callback function for odometry

        # print msg.pose.pose #print position and orientation of turtlebot
        self.odom_x = msg.pose.pose.position.x
        self.odom_y = msg.pose.pose.position.y

        rot_q = msg.pose.pose.orientation
        (roll, pitch, theta) = euler_from_quaternion([rot_q.x, rot_q.y, rot_q.z, rot_q.w])
        self.odom_theta = theta

    def move_sine(self):
        #fill here(from prev task)
        pass


if __name__ == '__main__':
    rospy.init_node('obstacle_avoidance_node') #initilize node


    rclass = Moving() #run class

    #move in the opp path(given eq)
    #and reach position (-10,0,0)

    # rclass.move_sine()

    #subscribe to the lidar to avoid obstacle
    # rclass.sub = rospy.Subscriber("/scan", LaserScan, self.callback)
    #move till (-25,0,0)

    rclass.linear_vel = 0.1
    rclass.go_to_goal(-25)






    # rospy.spin() #loop it