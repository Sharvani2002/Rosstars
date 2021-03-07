# Rosstars

Before running the tasks ensure that all the files in the `scripts` folder are executable:
`$chmod +x *` 
Also use `catkin_make` to build the packages and source setup the workspace after that

## Tasks completed:

### Task#1:
Youtube link:
https://youtu.be/koBg9EcM_EM

To check this task, run these:
```
$roslaunch embedathon2021 task1.launch
$rosrun embedathon2021 task1.py
```

### Task#2:
Youtube link:
https://youtu.be/hUf_AHrWGKU

To check this task, run these:
```
$roslaunch embedathon2021 task2.launch
$rosrun embedathon2021 task2.py
```


### Task#3:
- 3.1: 
 Youtube link: 
 https://youtu.be/es892odM_Xo
  
  To check this task, run these:
```
$roslaunch embedathon2021 task3.launch
$rosrun rosrun teleop_twist_keyboard teleop_twist_keyboard.py
```

- 3.2.1: 
 Youtube link: 
 https://youtu.be/hC0Ad-ikhnc
  
  To check this task, run these:
```
$roslaunch embedathon2021 temp.launch
$rosrun rosrun embedathon2021 task3-subtask1.py
```

- 3.2.2: https://youtu.be/o9VWxZO8c6Y

   To check this task, there are 2 ways we tried:
  
  - Method 1
    ```
    $roslaunch embedathon2021 task3.launch
    $rosrun rosrun embedathon2021 task3.py
    ```
  - Method 2
    ```
    $roslaunch embedathon2021 task3.launch
    $roslaunch embedathon2021 bug2.launch
    ```
    The python files used in this method are: 
    `bug_algo_2.py` , `follow_wall.py` and `go_to_point.py`
    
- To integrate 3.2.1 and 3.2.2 (Method 1):
   - comment `self.shutdown()` and other statements that cause break in loop in task3-subtask1.py file
   - copy the libraries and class from task3.py to task3-subtask1.py
   - copy the line `self.sub1 = rospy.Subscriber("/scan", LaserScan, self.callback)` from __init__ in task3.py to task3-subtask1.py
   - Copy these lines from main of task3.py to main of task3-subtask1.py file
     ```
      rclass = Moving() 
      rclass.linear_vel = 0.1
      rclass.go_to_goal(-25)
      ```
- NOTE: Task 3.3 can be done using 3.2.2 (Method 1 or 2), but the initial and final destination points need to be changed
