import numpy as np
import cv2

# Baike Shen 
# Jan-22-2018 Vancouver

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
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

# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    mask = cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1], img.shape[0]))
    
    return warped, mask


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
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
	
	
    # 2) Apply perspective transform
	warped, mask = perspect_transform(Rover.img, source, destination)	
	
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
	threshed_path, threshed_rock, threshed_obs = color_thresh(warped)
	obstacles_world = np.absolute(np.float32(threshed_obs)) * mask	
	
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
	Rover.vision_image[:,:,0] = obstacles_world * 255 #obstacles color-thresholded binary image
	Rover.vision_image[:,:,1] = threshed_rock * 255 #rocks color-thresholded binary image
	Rover.vision_image[:,:,2] = threshed_path * 255 #terrain color-thresholded binary images
	
    # 5) Convert map image pixel values to rover-centric coords
	xpix, ypix = rover_coords(threshed_path)            # Convert navigable path
	obs_xpix, obs_ypix = rover_coords(obstacles_world)  # Convert obstacle
	rock_xpix, rock_ypix = rover_coords(threshed_rock)	# Convert rocks
	
    # 6) Convert rover-centric pixel values to world coordinates
	x_world, y_world = pix_to_world(xpix,ypix,xpos,ypos,yaw,world_size,scale)                     # navigable path
	obs_xworld, obs_yworld = pix_to_world(obs_xpix,obs_ypix,xpos,ypos,yaw,world_size,scale)       # obstacle
	rock_xworld, rock_yworld = pix_to_world(rock_xpix,rock_ypix,xpos,ypos,yaw,world_size,scale)
	
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
	Rover.worldmap[obs_yworld, obs_xworld, 0] += 20
	Rover.worldmap[rock_yworld, rock_xworld, 1] += 10
	Rover.worldmap[y_world, x_world, 2] +=  20
	
    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
	rover_dist, rover_angles = to_polar_coords(xpix, ypix)
	
	# Update Rock pixel distances and angles
	# Assuming there is maximum only one rock seen by Rover.
	rock_dist, rock_angle = to_polar_coords(rock_xpix, rock_ypix)

	
    # Update distances and angle of Rover and Rock, respectively.
	Rover.nav_dists = rover_dist
	Rover.nav_angles = rover_angles
	Rover.rock_dists = rock_dist      # storing rock sample distances
	Rover.rock_angles = rock_angle	  #  and angle for Speeding up
 
    
    
	return Rover