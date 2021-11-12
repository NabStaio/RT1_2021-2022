#!/usr/bin/env python

from __future__ import print_function

import time
from sr.robot import *

a_th = 2.0
""" float: Threshold for the control of the linear distance"""

d_th = 0.4
""" float: Threshold for the control of the orientation"""

silver = True
""" boolean: variable for letting the robot know if it has to look for a silver or for a golden marker"""

R = Robot()
""" instance of the class Robot"""

def drive(speed, seconds):
    """
    Function for setting a linear velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


def turn(speed, seconds):
    """
    Function for setting an angular velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def clear_way(dist, rot_y):
	"""
	Function for detecting if there are golden boxes in a middle
	of a silver token's detection
	
	Args: dist(int) : distance retrieve by R.see()
	      rot_y (float) : angle between the robot and the silver token
	      
	Returns:
		True: Golden boxes are in the middle
		False: clear path
	"""
	for token in R.see():
		if  token.info.marker_type is MARKER_TOKEN_GOLD and rot_y-10 < token.rot_y < rot_y + 10 and token.dist < dist:
			return True
    	#print("FREE WAY")        		
	return False
	
def find_silver_token():
    """
    Function to find the closest silver token in a range vision of 180 degree 
    and in absence of golden boxes in the middle, a sort of clear path,
    checked with clear_way(dist, rot_y)

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    dist=100
    for token in R.see():
        if -90<=token.rot_y<=90 and token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER and not(clear_way(token.dist, token.rot_y)):
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y

def find_golden_token():
    """
    Function to find the closest golden token in a range of 15 degree in front of the robot

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """
    dist=100
    for token in R.see():
        if -7.5<token.rot_y<7.5 and token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y

def find_left_wall():
    """
    Function to find the left golden tokens (sensors' range with a delta of 15 degree with repect to 90 degree)

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """
    dist=100
    for token in R.see():
        if -105<token.rot_y<-75 and token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y

def find_right_wall():
    """
    Function to find the right golden tokens (sensors' range with a delta of 15 degree with respect to 90)

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """
    
    dist=100
    for token in R.see():
        if 75<token.rot_y<105 and token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y

def drive_safely():
    """
	Function to drive in a "safe" way the robot.
	
	It is call in the main function to guide the robot through the circuit
	avoiding collision with the golden tokens.
	It is retrieved the distances of the left, right and front wall with 
	respect to the robot.
	
	If it is near to right wall to a certain threshold, turn counter-clockwise.
	If it is near to left wall to a certain threshold, turn clockwise
	If it is in front of a wall control if it is a corner:
	if it is in a left corner, turn right of 90 degree
	If it is a right corner, turn left of 90 degree
	
    """

    dist_right = find_right_wall()[0]
    dist_left = find_left_wall()[0]
    dist_front = find_golden_token()[0]

    if dist_right < 0.75:
        turn(-5,1)
        #print("Turn counter-clockwise")
        drive(30,0.5)
    elif dist_left < 0.75:
        turn(5,1)
        #print("Turn clockwise")
        drive(30,0.5)
    elif dist_front < 0.9:
    	#print("I'm crushing")
        if dist_right < 2.5:
            turn(-30,1)
        elif dist_left < 2.5:
            turn(30,1)    
        
        drive(40,0.5)


    drive(50,0.1)    
    #print("I'm driving carefully")
    
    
    
########################################################################
# Here it is computed the main function                                #
# A while loop where the robot detects silver token in the arena and   #
# then drive in a carefully way to them.                               #
# Arguments passes numerically to the functions are chosen             #
# relative to the specific environment                                 #
########################################################################

while 1:
    
	dist, rot_y = find_silver_token() 
	#print for retrieve information about angle and distances to see if the conditions are met	
        #markers = R.see()
	#print ("I can see", len(markers), "markers:")
    	#for m in markers:
    		#if m.info.marker_type in (MARKER_TOKEN_SILVER):
    			#print( " - Angle {0} {1} metres away".format( m.rot_y, m.dist ))
        if(dist == -1):
        	#print("I see a handful of flies")
        	drive_safely()
        else:    
		drive_safely()
              	
        	if dist <d_th: # if we are close to the token, we try grab it.
        		print("Found it!")
        		if R.grab(): # if we grab the token, we move the robot forward and behind, we release the token, and we go back to the initial position
        	        	print("Gotcha!")
				turn(30, 1.999)
	                	drive(40,0.25)
	        		R.release()
                		drive(-40,0.25)
	            		turn(-30, 1.999)
                    	
	        	else:
                		print("Aww, I'm not close enough.")
        	elif -a_th<= rot_y <= a_th: # if the robot is well aligned with the token, we go forward
	        	print("Ah, that'll do.")
                	drive(100, 0.05)
        	elif rot_y < -a_th: # if the robot is not well aligned with the token, we move it on the left or on the right
        		print("Left a bit...")
                	turn(-8, 0.125)
        	elif rot_y > a_th:
                	print("Right a bit...")
        		turn(+8, 0.125)
	
