#! /usr/bin/env python

# import ros stuff
import rospy
# import ros message
from geometry_msgs.msg import Point
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from tf import transformations
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import SetModelState
# import ros service
from std_srvs.srv import *

import math

#define some global variables to store the goal and the current statu

srv_client_go_to_point_ = None
srv_client_wall_follower_ = None
yaw_ = 0
yaw_error_allowed_ = 5 * (math.pi / 180) # 5 degrees
position_ = Point()
initial_position_ = Point()

# initial_position_.x = rospy.get_param('initial_x')
# initial_position_.y =  rospy.get_param('initial_y')
initial_position_.x = -10
initial_position_.y = 0

initial_position_.z = 0
desired_position_ = Point()

# desired_position_.x = rospy.get_param('des_pos_x') #-25
# desired_position_.y = rospy.get_param('des_pos_y') # 0
desired_position_.x = -25
desired_position_.y = 0

desired_position_.z = 0
regions_ = None
state_desc_ = ['Go to point', 'wall following']
state_ = 0
count_state_time_ = 0 # seconds the robot is in a state
count_loop_ = 0
# 0 - go to point
# 1 - wall following

# Like in Bug 1 algorithm, we are storing the state of the robot. 
# I put some description of the states in an Array called state_desc_. 
# There are also 2 new arguments being received: initial_x and initial_y.
# They are used to restore the robot position in case you want to restart the algorithm.
# Very useful to test the algorithm many times in a row!

 

# Defining callbacks

def clbk_odom(msg):
    global position_, yaw_

    # position
    position_ = msg.pose.pose.position

    # yaw
    quaternion = (
        msg.pose.pose.orientation.x,
        msg.pose.pose.orientation.y,
        msg.pose.pose.orientation.z,
        msg.pose.pose.orientation.w)
    euler = transformations.euler_from_quaternion(quaternion)
    yaw_ = euler[2]

def clbk_laser(msg):

    global regions_
    regions_ = {
        'bright':  min(min(msg.ranges[0:71]), 2),
        'fright': min(min(msg.ranges[72:143]), 2),
        'front':  min(min(msg.ranges[144:215]), 2),
        'fleft':  min(min(msg.ranges[216:287]), 2),
        'bleft':   min(min(msg.ranges[288:359]), 2),
    }
 

# Helper functions
# The first helper function is change_state.

def change_state(state):
    global state_, state_desc_
    global srv_client_wall_follower_, srv_client_go_to_point_
    global count_state_time_
    count_state_time_ = 0
    state_ = state
    log = "state changed: %s" % state_desc_[state]
    rospy.loginfo(log)
    if state_ == 0:
        resp = srv_client_go_to_point_(True)
        resp = srv_client_wall_follower_(False)
    if state_ == 1:
        resp = srv_client_go_to_point_(False)
        resp = srv_client_wall_follower_(True)


# We have only 2 states: wall_follower and go_to_point. 
# The different is that we are not driving the robot in a straight line to the desired point,
# but following the original line. The one from the initial position to the desired one. 
# This will be implemented on the main function.

# The next one: distance_to_line:

def distance_to_line(p0):
    # p0 is the current position
    # p1 and p2 points define the line
    global initial_position_, desired_position_
    p1 = initial_position_
    p2 = desired_position_
    # here goes the equation
    up_eq = math.fabs((p2.y - p1.y) * p0.x - (p2.x - p1.x) * p0.y + (p2.x * p1.y) - (p2.y * p1.x))
    lo_eq = math.sqrt(pow(p2.y - p1.y, 2) + pow(p2.x - p1.x, 2))
    distance = up_eq / lo_eq

    return distance

def normalize_angle(angle):
    if(math.fabs(angle) > math.pi):
        angle = angle - (2 * math.pi * angle) / (math.fabs(angle))
    return angle

#Part- 1
def main():
    global regions_, position_, desired_position_, state_, yaw_, yaw_error_allowed_
    global srv_client_go_to_point_, srv_client_wall_follower_
    global count_state_time_, count_loop_

    rospy.init_node('bug_algo_2')

    sub_laser = rospy.Subscriber('/scan', LaserScan, clbk_laser)
    sub_odom = rospy.Subscriber('/odom', Odometry, clbk_odom)

    rospy.wait_for_service('/go_to_point_switch')
    rospy.wait_for_service('/wall_follower_switch')
    rospy.wait_for_service('/gazebo/set_model_state')

    srv_client_go_to_point_ = rospy.ServiceProxy('/go_to_point_switch', SetBool)
    srv_client_wall_follower_ = rospy.ServiceProxy('/wall_follower_switch', SetBool)
    srv_client_set_model_state = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState)

    # set robot position
    model_state = ModelState()
    model_state.model_name = 'turtlebot3_waffle_pi'#'mybot_spawn'#'#.._sim' #arena_task3 #'m2wr'
    model_state.pose.position.x = initial_position_.x
    model_state.pose.position.y = initial_position_.y
    resp = srv_client_set_model_state(model_state)

    # initialize going to the point
    change_state(0)

    rate = rospy.Rate(20)


#Part -2 loop logic
    while not rospy.is_shutdown():
        if regions_ == None:
            continue

        distance_position_to_line = distance_to_line(position_)

        if state_ == 0:
            if regions_['front'] > 0.15 and regions_['front'] < 1:
                change_state(1)

        elif state_ == 1:
            if count_state_time_ > 5 and distance_position_to_line < 0.1:
                change_state(0)

        count_loop_ = count_loop_ + 1
        if count_loop_ == 20:
            count_state_time_ = count_state_time_ + 1
            count_loop_ = 0

        rospy.loginfo("distance to line: [%.2f], position: [%.2f, %.2f]", distance_to_line(position_), position_.x, position_.y)
        rate.sleep()