#!/usr/bin/env python

from astropy.time import Time, TimeDelta
from astropy import units as u
import inspect

from propagator_module import PropagatorModule
from visibility_module import VisibilityModule
from visualisation_module import VisualisationModule
from scheduling_module import SchedulingModule

# Dictionary to store variables from main function
# (allows viewing through the variable explorer)
local_vars = {}

# TODO: copyright notices

plot_bitmaps = False

def main():
    # Set parameters
    start_time = Time("2021-03-20 12:00")
    end_time = Time("2021-03-20 12:10")
    time_step = TimeDelta(5*u.min)
    keplerian_elements = {"SMA": 7000,
                          "ECC": 0,
                          "INC": 98.6,
                          "RAAN": 90,
                          "AOP": 0,
                          "TA": 0}

    # Run orbit propagation
    propagator = PropagatorModule(start_time,
                                  end_time,
                                  time_step,
                                  keplerian_elements)
    propagator.propagate_spacecraft()
    propagator.get_solar_bodies()

    # Calculate target visibility
    visibility = VisibilityModule(propagator.spacecraft_frame,
                                  propagator.solar_bodies)
    visibility.get_targets()
    visibility.calculate_visibility()
    visibility.calculate_contacts()
    visibility.calculate_overall_stats()

    # Plot telescope visibility
    visualisation = VisualisationModule(propagator.spacecraft_frame,
                                        visibility.solar_bodies,
                                        visibility.targets,
                                        cuda=True)
    if plot_bitmaps:
        visualisation.generate_bitmaps()
        visualisation.plot_bitmaps()
        
    # Schedule observations
    scheduling = SchedulingModule(visibility.targets)
    scheduling.combine_contacts()
    scheduling.simple_dynamic_schedule()

    # Store local variables
    global local_vars
    local_vars = inspect.currentframe().f_locals


# Run if main file
if __name__ == "__main__":
    main()
