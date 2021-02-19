#!/usr/bin/env python

from astropy.time import Time
import inspect

from gmatInterface import gmatInterface
from visibilityModule import visibilityModule

# Dictionary to store variables from main function
# (allows viewing through the variable explorer)
local_vars = {}

def main():
    # Set parameters
    start_time = Time("2021-03-20 12:00")
    end_time = Time("2021-03-27 12:00")
    keplerian_elements = {"SMA": 7000,
                          "ECC": 0,
                          "INC": 98.6,
                          "RAAN": 90,
                          "AOP": 0,
                          "TA": 0}
    
    # Run orbit propagation
    gmat = gmatInterface(start_time, end_time, keplerian_elements)
    gmat.generate_script()
    gmat.execute_script()
    gmat.load_state()
    
    # Calculate target visibility
    visibility = visibilityModule(gmat.satellite_frame)
    visibility.get_solar_bodies()
    visibility.get_targets()
    visibility.calculate_visibility()
    
    # Store local variables
    global local_vars
    local_vars = inspect.currentframe().f_locals

# Run if main file
if __name__ == "__main__":
    main()