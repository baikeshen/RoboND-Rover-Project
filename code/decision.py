import numpy as np



# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!
    
    

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if len(Rover.rock_angles) != 0:
            Rover.sample_pos_found = Rover.rock_angles   # extra variable for storing the angle of rock sample
            Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
            if len(Rover.rock_angles) >= 20:             # 
                Rover.sample_pos_found = Rover.rock_dists
                
                if Rover.vel < 1:      # low speed
                # Set throttle value to throttle setting
                    Rover.throttle = 0.1
                    Rover.brake = 0
                elif Rover.vel >= 1:
                    Rover.brake = 5
                    Rover.throttle = 0
                else: 
                    Rover.throttle = 0
                Rover.brake = 0
                
            elif len(Rover.rock_angles) <= 20:  # within steering angle
                Rover.sample_pos_found = len(Rover.rock_angles)
                # Set mode to "stop" and hit the brakes!
                # Rover.throttle = 0
                if Rover.vel < 0.5:   #lower speed
                # Set throttle value to throttle setting
                    Rover.throttle = 0.1
                    Rover.brake = 0
                elif Rover.vel >= 0.5:
                    Rover.throttle = 0
                    Rover.brake = 5
                else: # Else coast
                    Rover.throttle = 0              
                # Set brake to stored brake value 
                if Rover.near_sample:    # ready to pickup
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
                        Rover.send_pickup = True
                        
        elif Rover.mode == 'forward' and Rover.near_sample == 0:   
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
                
                # If no enough navigable terrain pixels,  go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                # Set mode to "stop" and hit the brakes!
                Rover.throttle = 0
                # Set brake to stored brake value
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'

            # If in "stop" mode, then make different decisions
        elif Rover.mode == 'stop':      
            
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If vel < 0.2 then do something else
            elif Rover.vel <= 0.2:
                # check if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -25 
               
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

