## Name: forest_fire_sim
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

P_CHAPARRAL = 0.093
P_FOREST = 0.018
P_CANYON = 1
FIREBRAND = 0.05
FIREBRAND_DECAY = FIREBRAND/3
WIND_FACTOR = 1


"""
1 gen 15 mins
canyon 6 hrs
chaparral 6 days
forest 25 days

"""
DECAY_CANYON = 24
DECAY_FOREST = DECAY_CANYON * 50
DECAY_CHAPARRAL = DECAY_CANYON * 12


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
    config.grid_dims = (100,100)

    grid = np.zeros((100,100))
    
    #setting forest
    for x in range(30,50):
        for y in range(9,35):
            grid[y][x] = 2
    for x in range(0,50):
        for y in range(40,70):
            grid[y][x] = 2

    #setting canyon
    for x in range(60,65):
        for y in range(10,80):
            grid[y][x] = 1

    #setting lake
    for x in range(10,50):
        for y in range(35,40):
            grid[y][x] = 3

    #setting town
    for x in range(37,42):
        for y in range(87,92):
            grid[y][x] = 4

    #powerplant
    grid[0][0] = 5

    #incinerator
    grid[0][99] = 5
    


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


def transition_function(grid, neighbourstates, neighbourcounts, decaygrid, firebrandgrid):
    """Function to apply the transition rules
    and return the new grid"""
    # 0:chaparral
    # 1:canyon
    # 2:forest
    # 3:lake
    # 4:town
    # 5:burning
    # 6:burnt
    # YOUR CODE HERE
    NW, N, NE, W, E, SW, S, SE = neighbourstates

    #N,W,E,S = neighbourstates

    chaparral_states = (grid == 0)
    canyon_states = (grid == 1)
    forest_states = (grid == 2)
    burning_states = (grid == 5)

    burning_neighbor_counts = neighbourcounts[5]


    #states with the neighbor to its north burning
    wind_direction_burning = (N == 5)

    firebrandgrid = firebrand(neighbourstates, firebrandgrid)

    p_forest = P_FOREST
    p_chaparral = P_CHAPARRAL
    p_canyon = P_CANYON
    

    start_burning_forest = check_burn2(forest_states, burning_neighbor_counts, p_forest, firebrandgrid, wind_direction_burning, burning_states)
    start_burning_chaparral = check_burn2(chaparral_states, burning_neighbor_counts, p_chaparral, firebrandgrid, wind_direction_burning, burning_states)
    start_burning_canyon = check_burn2(canyon_states, burning_neighbor_counts, p_canyon, firebrandgrid, wind_direction_burning, burning_states)
    start_burning = start_burning_chaparral | start_burning_canyon | start_burning_forest

    decaygrid[burning_states] -= 1
    decayed_to_zero = (decaygrid == 0)
    grid[start_burning] = 5
    grid[decayed_to_zero] = 6

        

    """

    PROBABALISTIC MODEL 1

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
    
    

    fourm_burning = (neighbourcounts[5] >= 4)

    onem_burning = (neighbourcounts[5] >= 1)

    # start_burning = check_burn(forest_states, eight_burning, p_forest, firebrandgrid, 8)
    # start_burning = start_burning | (check_burn(forest_states, seven_burning, p_forest, firebrandgrid, 7))
    # start_burning = start_burning | (check_burn(forest_states, six_burning, p_forest, firebrandgrid, 6))
    # start_burning = start_burning | (check_burn(forest_states, five_burning, p_forest, firebrandgrid, 5))
    # start_burning = start_burning | (check_burn(forest_states, four_burning, p_forest, firebrandgrid, 4))
    # start_burning = start_burning | (check_burn(forest_states, three_burning, p_forest, firebrandgrid, 3))
    # start_burning = start_burning | (check_burn(forest_states, two_burning, p_forest, firebrandgrid, 2))
    # start_burning = start_burning | (check_burn(forest_states, one_burning, p_forest, firebrandgrid, 1))

    # start_burning = start_burning | (check_burn(chaparral_states, fourm_burning, p_chaparral, firebrandgrid))
    # start_burning = start_burning | (check_burn(chaparral_states, three_burning, p_chaparral, firebrandgrid))
    # start_burning = start_burning | (check_burn(chaparral_states, two_burning, p_chaparral, firebrandgrid))
    # start_burning = start_burning | (check_burn(chaparral_states, one_burning, p_chaparral, firebrandgrid))

    # start_burning = start_burning | (check_burn(canyon_states, onem_burning, 1, firebrandgrid))



    DETERMINISTIC MODEL

    #states with three or more neighbors burning
    three_burning = (neighbourcounts[5] >= 3)
    #states with two or more neighbors burning
    two_burning = (neighbourcounts[5] >= 2)
    #states with one or more neighbors burning
    one_burning =(neighbourcounts[5] >= 1)
    #states with the neighbor to its north burning
    wind_direction_burning = (N == 5)

    
    wind version 1
        canyon burns as long as there is one neighbor(does not have to be from the north)
        chaparral needs two neighbors burning OR just one neighbor from the north
        forest needs three neighbors OR one neighbor from the top and at least one other neighbor burning
    
    #start_burning = (canyon_states & one_burning) | ((chaparral_states & two_burning) | (chaparral_states & wind_direction_burning)) | ((forest_states & three_burning) | (forest_states & (wind_direction_burning & two_burning)))
    
    #no wind
    start_burning = (canyon_states & one_burning) | ((chaparral_states & two_burning)) | ((forest_states & three_burning))
    """
    return grid
"""
def check_burn(land_states, burning_neighbors, probability, firebrandgrid, burning_neighbor_count):
    check_burnable = (land_states & burning_neighbors)
    p = 1 - ((1 - p)**burning_neighbor_count)
    check_burnable = np.reshape(check_burnable, 10000)
    firebrandgrid_reshaped = np.reshape(firebrandgrid, 10000)

    for i in range(10000):
        if check_burnable[i]:
            x = random.random()
            if x > (probability + firebrandgrid_reshaped[i]):
                check_burnable[i] = False

    final_burning = np.reshape(check_burnable, (100,100))
    return final_burning"""

def check_burn2(land_states, burning_neighbor_counts, probability, firebrandgrid, wind_burning, burning_states):
    for x in range(100):
        for y in range(100):
            if land_states[y][x]:
                z = random.random()
                num_neighbors = burning_neighbor_counts[y][x]
                firebrand_p = firebrandgrid[y][x]
                if wind_burning[y][x]:
                    p = 1 - ((1 - probability)**(num_neighbors+WIND_FACTOR)) + firebrand_p
                else:
                    p = 1 - ((1 - probability)**(num_neighbors)) + firebrand_p
                if z < p:
                    burning_states[y][x] = True
    return burning_states


def firebrand(neighbourstates, firebrandgrid):
    NW, N, NE, W, E, SW, S, SE = neighbourstates
    #N,W,E,S = neighbourstates
    north_burning = (N==5)
    for x in range(100):
        for y in range(1, 100):
            if north_burning[y][x]:
                firebrandgrid[y][x] = FIREBRAND
            elif (firebrandgrid[y-1][x] != 0):
                firebrandgrid[y][x] = firebrandgrid[y-1][x] - FIREBRAND_DECAY
            else:
                firebrandgrid[y][x] = 0
    return firebrandgrid
    

def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    decaygrid = np.zeros(config.grid_dims)
    decaygrid.fill(-1)
    temp_grid = (config.initial_grid == 0)
    decaygrid[temp_grid] = DECAY_CHAPARRAL
    temp_grid = (config.initial_grid == 1)
    decaygrid[temp_grid] = DECAY_CANYON
    temp_grid = (config.initial_grid == 2)
    decaygrid[temp_grid] = DECAY_FOREST

    firebrandgrid = np.zeros(config.grid_dims)
    firebrandgrid.fill(0)

    # Create grid object using parameters from config + transition function
    grid = Grid2D(config, (transition_function, decaygrid, firebrandgrid))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
