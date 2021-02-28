#!/usr/bin/env python

from astropy.time import Time
import inspect

from propagatorModule import propagatorModule
from visibilityModule import visibilityModule
from visualisationModule import visualisationModule

# Dictionary to store variables from main function
# (allows viewing through the variable explorer)
local_vars = {}

# TODO: copyright notices

def main():
    # Set parameters
    start_time = Time("2021-03-20 12:00")
    end_time = Time("2021-03-20 13:00")
    keplerian_elements = {"SMA": 7000,
                          "ECC": 0,
                          "INC": 98.6,
                          "RAAN": 90,
                          "AOP": 0,
                          "TA": 0}

    # Run orbit propagation
    propagator = propagatorModule(start_time, end_time, keplerian_elements)
    propagator.propagate_spacecraft()
    propagator.get_solar_bodies()

    # Calculate target visibility
    visibility = visibilityModule(propagator.spacecraft_frame,
                                  propagator.solar_bodies)
    visibility.get_targets()
    visibility.calculate_visibility()

    # Plot telescope visibility
    visualisation = visualisationModule(propagator.spacecraft_frame,
                                        visibility.solar_bodies,
                                        visibility.targets)
    visualisation.generate_bitmaps()
    visualisation.plot_bitmaps()

    # Store local variables
    global local_vars
    local_vars = inspect.currentframe().f_locals


# Run if main file
if __name__ == "__main__":
    main()
