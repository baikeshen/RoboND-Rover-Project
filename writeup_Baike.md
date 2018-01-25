## Project: Search and Sample Return
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./misc/fig1.png
[image2]: ./misc/fig2.png
[image3]: ./misc/fig3.png
[image4]: ./misc/fig4.png
[image5]: ./misc/fig5.png
[image6]: ./misc/test_mapping_v1.mp4


## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Obstacle and rock sample identification.

Color thresholding Function:

Obstacle and rock sample identification was done by using the function of color_thresh_range. Color thresholding means that color values, which falll within a given range, are given a desired color. In my case, three threshold ranges have been used, one for the navigable terrain, another one for obstacle, and the last one for rock sample. 

'''

def color_thresh(img, rgb_thresh=(160, 160, 160, 110, 110, 50)):
    # Create an array of zeros same xy size as img, but single channel
    # color_select = np.zeros_like(img[:,:,0])
    color_select_path = np.zeros_like(img[:,:,0])
    color_select_rock = np.zeros_like(img[:,:,0])
    color_select_obstacle = np.zeros_like(img[:,:,0])	
    
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    # Threshold for navigable path:
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    
    # Threshold for rocks
    rock_thresh = (img[:,:,0] > rgb_thresh[3] ) \
                & (img[:,:,1] > rgb_thresh[4] ) \
                & (img[:,:,2] < rgb_thresh[5] )
    
    # Threshold for obstacles
    obs_thresh = (img[:,:,0] < rgb_thresh[0]) \
                & (img[:,:,1] < rgb_thresh[1]) \
                & (img[:,:,2] < rgb_thresh[2])				
    
    # Index the array of zeros with the boolean array and set to 1vigab
    # color_select[above_thresh] = 1
    
    color_select_path[above_thresh] = 1
    color_select_rock[rock_thresh] = 1
    color_select_obstacle[obs_thresh] = 1	
    # Return the binary image
    return  color_select_path, color_select_rock, color_select_obstacle

'''

![alt text][image2]


**Perspective Transform

With knowing what pixels in an image belong to either navigiable path, rock samples, or obstacles, it is required to find out where each pixel is located in relation to the Rover. The code used for warping can be found as follows: 

'''
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    mask = cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1], img.shape[0]))
    return warped, outView
'''

![alt text][image3]

Next Image

![alt text][image4]

Next Image

![alt text][image5]

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 

![alt text][image6]

Due to some technical issues, the model of moviepy can not be installed on my computer. Although the code section of process_image has been written, there is no result available to be attached. The code is shown as below:

'''
def process_image(img):
    #Example of how to use the Databucket() object defined above
    #to print the current x, y and yaw values 
    #print(data.xpos[data.count], data.ypos[data.count], data.yaw[data.count])
    
    dst_size = 8   # played with dst_size to test which one would fit the mapping
    
    #TODO: 
    #1) Define source and destination points for perspective transform
    #2) Apply perspective transform
    warped, mask = perspect_transform(img, source, destination)
    
    #3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    threshed_path, threshed_rock, threshed_obs = BK_color_thresh(warped)
    obstacles_world = np.absolute(np.float32(threshed_obs))*mask
    
    #4) Convert thresholded image pixel values to rover-centric coords
    xpix, ypix = rover_coords(threshed_path)    
    
    #5) Convert rover-centric pixel values to world coords
    world_size = data.worldmap.shape[0]
    scale = 2*dst_size
    xpos = data.xpos[data.count]
    ypos = data.ypos[data.count]
    yaw = data.yaw[data.count]
    x_world, y_world = pix_to_world(xpix,ypix,xpos,ypos,yaw,world_size,scale)
    
    obs_xpix, obs_ypix = rover_coords(obstacles_world)
    obs_xworld, obs_yworld = pix_to_world(obs_xpix,obs_ypix,xpos,ypos,yaw,world_size,scale)
    
    rock_xpix, rock_ypix = rover_coords(threshed_rock)
    rock_xworld, rock_yworld = pix_to_world(rock_xpix,rock_ypix,xpos,ypos,yaw,world_size,scale)    
    
    #6) Update worldmap (to be displayed on right side of screen)
        #Example: data.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #data.worldmap[rock_y_world, rock_x_world, 1] += 1
        #data.worldmap[navigable_y_world, navigable_x_world, 2] += 1
        
    data.worldmap[y_world, x_world,2] = 255
    data.worldmap[obs_yworld,obs_xworld,0] = 255
    
    data.worldmap[rock_yworld,rock_xworld,1] = 255        
    
    #below, these two methods prevent the obstacle areas to overwrite the path area.
    nav_pix = data.worldmap[:,:,2] > 0
    data.worldmap[nav_pix, 0] = 0
    
    
    #7) Make a mosaic image, below is some example code
        #First create a blank image (can be whatever shape you like)
    output_image = np.zeros((img.shape[0] + data.worldmap.shape[0], img.shape[1]*2, 3))
        #Next you can populate regions of the image with various output
        #Here I'm putting the original image in the upper left hand corner
    output_image[0:img.shape[0], 0:img.shape[1]] = img

        # Let's create more images to add to the mosaic, first a warped image
    warped = perspect_transform(img, source, destination)
        #Add the warped image in the upper right hand corner
    output_image[0:img.shape[0], img.shape[1]:] = warped

        # Overlay worldmap with ground truth map
    map_add = cv2.addWeighted(data.worldmap, 1, data.ground_truth, 0.5, 0)
        #Flip map overlay so y-axis points upward and add to output_image 
    output_image[img.shape[0]:, 0:data.worldmap.shape[1]] = np.flipud(map_add)


        # Then putting some text over the image
    cv2.putText(output_image,"Populate this image with your analyses to make a video!", (20, 20), 
                cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
    if data.count < len(data.images) - 1:
        data.count += 1 # Keep track of the index in the Databucket()
    
    return output_image
    
'''

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

**drive_rover.py modification**

some extra variables have been added for storing rock sample angles and distances:

'''
    def __init__(self):
        self.start_time = None # To record the start time of navigation
        self.total_time = None # To record total duration of naviagation

        
        #self defined extra varaible
        #these changes to provide the extra variables to the rover for storing rock distances and angles
        #an addition string variable used for testing and debugging purposes

        self.sample_pos_found = None # to print string of sample pos situation
        self.rock_angles = 0 # rock angles used in perception_step
        self.rock_dists =  0 # rock distances used in perception_step
        #end of self defined variable
        

'''

**perception.py modification:**

Three thresholds have been used for navigiable path, rock examples, and obstabccles. In order to recognize the yellow pixels from the rock examples, red and green thresholds shall be higher than 110 but the blue thershold shall be lower than 50:

'''
def color_thresh(img, rgb_thresh=(160, 160, 160, 110, 110, 50)):
    #Create an array of zeros same xy size as img, but single channel
    #color_select = np.zeros_like(img[:,:,0])
    color_select_path = np.zeros_like(img[:,:,0])
    color_select_rock = np.zeros_like(img[:,:,0])
    color_select_obstacle = np.zeros_like(img[:,:,0])	
	
    #Require that each pixel be above all three threshold values in RGB
    #above_thresh will now contain a boolean array with "True"
    #where threshold was met
	#Threshold for navigable path:
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
				
	#Threshold for rocks
    rock_thresh = (img[:,:,0] > rgb_thresh[3] ) \
                & (img[:,:,1] > rgb_thresh[4] ) \
                & (img[:,:,2] < rgb_thresh[5] )
				
	#Threshold for obstacles
    obs_thresh = (img[:,:,0] < rgb_thresh[0]) \
                & (img[:,:,1] < rgb_thresh[1]) \
                & (img[:,:,2] < rgb_thresh[2])	
'''

The perspective_transform function is slightly modified to produce a second output(mask):

'''
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    mask = cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1], img.shape[0]))
    
    return warped, mask

'''

The major modifications have been implemmented in the perception_step() function. This function provides a complete computer vision which tells the navigaible path, steering direction, and the location of rock samples. Furthermore, two new variables (Rover.dists and Rover.angles) are provided to guide the Rover where the rock samples are for the purpose of steering.

'''
#Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    #Perform perception steps to update Rover()
    #TODO: 
    #NOTE: camera image is coming to you in Rover.img
    #1) Define source and destination points for perspective transform
	xpos, ypos = Rover.pos
	yaw = Rover.yaw
	dst_size=5
	bottom_offset=6
	world_size = Rover.worldmap.shape[0]
	scale = 2* dst_size
	source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
	destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
					[Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
					[Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], 
					[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
					])	
	
	
    #2) Apply perspective transform
	warped, mask = perspect_transform(Rover.img, source, destination)	
	
    #3) Apply color threshold to identify navigable terrain/obstacles/rock samples
	threshed_path, threshed_rock, threshed_obs = color_thresh(warped)
	obstacles_world = np.absolute(np.float32(threshed_obs)) * mask	
	
    #4) Update Rover.vision_image (this will be displayed on left side of screen)
        #Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #a          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #b          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
	Rover.vision_image[:,:,0] = obstacles_world * 255 #obstacles color-thresholded binary image
	Rover.vision_image[:,:,1] = threshed_rock * 255 #rocks color-thresholded binary image
	Rover.vision_image[:,:,2] = threshed_path * 255 #terrain color-thresholded binary images
	
    #5) Convert map image pixel values to rover-centric coords
	xpix, ypix = rover_coords(threshed_path)            # Convert navigable path
	obs_xpix, obs_ypix = rover_coords(obstacles_world)  # Convert obstacle
	rock_xpix, rock_ypix = rover_coords(threshed_rock)	# Convert rocks
	
    #6) Convert rover-centric pixel values to world coordinates
	x_world, y_world = pix_to_world(xpix,ypix,xpos,ypos,yaw,world_size,scale)                     # navigable path
	obs_xworld, obs_yworld = pix_to_world(obs_xpix,obs_ypix,xpos,ypos,yaw,world_size,scale)       # obstacle
	rock_xworld, rock_yworld = pix_to_world(rock_xpix,rock_ypix,xpos,ypos,yaw,world_size,scale)
	
    #7) Update Rover worldmap (to be displayed on right side of screen)
        #Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #a         Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #b          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
	Rover.worldmap[obs_yworld, obs_xworld, 0] += 20
	Rover.worldmap[rock_yworld, rock_xworld, 1] += 10
	Rover.worldmap[y_world, x_world, 2] +=  20
	
    #8) Convert rover-centric pixel positions to polar coordinates
    #Update Rover pixel distances and angles
        #Rover.nav_dists = rover_centric_pixel_distances
        #Rover.nav_angles = rover_centric_angles
	rover_dist, rover_angles = to_polar_coords(xpix, ypix)
	
	#Update Rock pixel distances and angles
	#Assuming there is maximum only one rock seen by Rover.
	rock_dist, rock_angle = to_polar_coords(rock_xpix, rock_ypix)

	
    #Update distances and angle of Rover and Rock, respectively.
	Rover.nav_dists = rover_dist
	Rover.nav_angles = rover_angles
	Rover.rock_dists = rock_dist      # storing rock sample distances
	Rover.rock_angles = rock_angle	  #  and angle for Speeding up
 
    
    
	return Rover

'''

**decision.py modification**

Some extra capabilities of locating and steering towards rock samples have been provided by using two new variables defined in the drive_rover.py. When Rover finds the rock samples, it stops when close to rock sample, and then pickups the samples.

'''
import numpy as np


def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if len(Rover.rock_angles) != 0:
            Rover.sample_pos_found = Rover.rock_angles
            Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
            if len(Rover.rock_angles) >= 20:
                Rover.sample_pos_found = Rover.rock_dists
                if Rover.vel < 1:
                # Set throttle value to throttle setting
                    Rover.throttle = 0.1
                    Rover.brake = 0
                elif Rover.vel >= 1:
                    Rover.brake = 5
                    Rover.throttle = 0
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
            elif len(Rover.rock_angles) <= 20:
                Rover.sample_pos_found = len(Rover.rock_angles)
                # Set mode to "stop" and hit the brakes!
                #Rover.throttle = 0
                if Rover.vel < 0.5:
                # Set throttle value to throttle setting
                    Rover.throttle = 0.1
                    Rover.brake = 0
                elif Rover.vel >= 0.5:
                    Rover.throttle = 0
                    Rover.brake = 5
                else: # Else coast
                    Rover.throttle = 0              
                # Set brake to stored brake value
                if Rover.near_sample:
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
                        Rover.send_pickup = True
        elif Rover.mode == 'forward' and Rover.near_sample == 0:   # and len(Rover.rock_angles) == 0
            Rover.sample_pos_found = len(Rover.rock_angles)
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set

                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                # Set mode to "stop" and hit the brakes!
                Rover.throttle = 0
                # Set brake to stored brake value
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'

            # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':      # and len(Rover.rock_angles) == 0
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -25 # just try one method
                # If we're stopped but see sufficient navigable terrain in front then go!
                elif len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward' 

    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
    
    return Rover

'''




**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

 Results of Autonomous mapping

Running the Rover in autonomous mode at 800X600 resolution, has resulted in map coverage that exceeding 55% and fidelity values exceeding 70%.


Potential improvements

To improve the covered arae can be done by providing a more sophisicated decision tree. Based on my method, Rover may go back the area where it went before. If it remebers where it has been in the past, so that it only explore the unvisted area if possible. This would result in higher coverage area.




![alt text][image6]


