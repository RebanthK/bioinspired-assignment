# Name: forest_fire_sim
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils
import numpy as np
import random
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "forest_fire_sim"
    config.dimensions = 2
    config.states = (0, 1, 2, 3, 4, 5, 6)
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0.4,1,0),(0.75,0.83,0),(0,0.54,0),(0,0.67,1),(0.9,0,1),(1,0,0),(0,0,0)]
    config.grid_dims = (200,200)

    grid = np.zeros((200,200))
    
    #setting forest
    for x in range(60,100):
        for y in range(19,70):
            grid[y,x] = 2
    for x in range(0,100):
        for y in range(80,140):
            grid[y,x] = 2

    #setting canyon
    for x in range(120,130):
        for y in range(20,160):
            grid[y,x] = 1

    #setting lake
    for x in range(20,100):
        for y in range(70,80):
            grid[y,x] = 3

    #setting town
    for x in range(75,85):
        for y in range(175,185):
            grid[y,x] = 4
    
    #powerplant
    grid[0,0] = 5
    # grid[1,0] = 5
    # grid[0,1] = 5
    # grid[1,1] = 5

    #incinerator
    #grid[0,199] = 5
    
    config.initial_grid = grid

    config.wrap = False

    # ----------------------------------------------------------------------

    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config


def transition_function(grid, neighbourstates, neighbourcounts):
    """Function to apply the transition rules
    and return the new grid"""
    # 0:chapparal
    # 1:canyon
    # 2:forest
    # 3:lake
    # 4:town
    # 5:burning
    # 6:burnt
    # YOUR CODE HERE

    NW, N, NE, W, E, SW, S, SE = neighbourstates

    chapparal_states = (grid == 0)
    canyon_states = (grid == 1)
    forest_states = (grid == 2)

    #states with eight or more neighbors burning
    eight_burning = (neighbourcounts[5] == 8)
    #states with seven or more neighbors burning
    seven_burning = (neighbourcounts[5] == 7)
    #states with six or more neighbors burning
    six_burning = (neighbourcounts[5] == 6)
    #states with three or more neighbors burning
    five_burning = (neighbourcounts[5] == 5)
    #states with four or more neighbors burning
    four_burning = (neighbourcounts[5] == 4)
    #states with three or more neighbors burning
    three_burning = (neighbourcounts[5] == 3)
    #states with two or more neighbors burning
    two_burning = (neighbourcounts[5] == 2)
    #states with one or more neighbors burning
    one_burning =(neighbourcounts[5] == 1)
    #states with the neighbor to its north burning
    northern_burning = (N == 5)

    fourm_burning = (neighbourcounts[5] >= 4)

    onem_burning = (neighbourcounts[5] >= 1)


    start_burning = forest_states & eight_burning

    start_burning = start_burning | (check_burn(forest_states, seven_burning, 0.5))
    start_burning = start_burning | (check_burn(forest_states, six_burning, 0.45))
    start_burning = start_burning | (check_burn(forest_states, five_burning, 0.4))
    start_burning = start_burning | (check_burn(forest_states, four_burning, 0.35))
    start_burning = start_burning | (check_burn(forest_states, three_burning, 0.3))
    start_burning = start_burning | (check_burn(forest_states, two_burning, 0.25))
    start_burning = start_burning | (check_burn(forest_states, one_burning, 0.2))

    start_burning = start_burning | (check_burn(chapparal_states, fourm_burning, 0.5))
    start_burning = start_burning | (check_burn(chapparal_states, three_burning, 0.45))
    start_burning = start_burning | (check_burn(chapparal_states, two_burning, 0.4))
    start_burning = start_burning | (check_burn(chapparal_states, one_burning, 0.35))

    start_burning = start_burning | (check_burn(canyon_states, onem_burning, 1))

        

    """
    DETERMINISTIC MODEL

    #states with three or more neighbors burning
    three_burning = (neighbourcounts[5] >= 3)
    #states with two or more neighbors burning
    two_burning = (neighbourcounts[5] >= 2)
    #states with one or more neighbors burning
    one_burning =(neighbourcounts[5] >= 1)
    #states with the neighbor to its north burning
    northern_burning = (N == 5)

    
    wind version 1
        canyon burns as long as there is one neighbor(does not have to be from the north)
        chapparal needs two neighbors burning OR just one neighbor from the north
        forest needs three neighbors OR one neighbor from the top and at least one other neighbor burning
    
    #start_burning = (canyon_states & one_burning) | ((chapparal_states & two_burning) | (chapparal_states & northern_burning)) | ((forest_states & three_burning) | (forest_states & (northern_burning & two_burning)))
    
    #no wind
    start_burning = (canyon_states & one_burning) | ((chapparal_states & two_burning)) | ((forest_states & three_burning))
    """
    grid[start_burning] = 5
    return grid

def check_burn(land_states, burning_neighbours, probability):
    check_burnable = (land_states & burning_neighbours)
    check_burnable = np.reshape(check_burnable, 40000)

    for i in range(40000):
        if check_burnable[i]:
            x = random.random()
            if x > probability:
                check_burnable[i] = False

    final_burning = np.reshape(check_burnable, (200,200))
    return final_burning

def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    # Create grid object using parameters from config + transition function
    grid = Grid2D(config, transition_function)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
