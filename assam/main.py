#!/usr/bin/env python

"""
MIT License

Copyright (c) 2020-2021 Max Hallgarten La Casta

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, IARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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

plot_bitmaps = False


def main():
    # Set parameters
    start_time = Time("2021-03-20 12:00")
    end_time = Time("2021-04-20 12:00")
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

    # Schedule observations
    scheduling = SchedulingModule(visibility.targets)
    scheduling.combine_contacts()
    scheduling.simple_dynamic_schedule()

    # Plot telescope visibility
    visualisation = VisualisationModule(propagator.spacecraft_frame,
                                        visibility.solar_bodies,
                                        visibility.targets,
                                        cuda=True)
    if plot_bitmaps:
        visualisation.generate_bitmaps()
        visualisation.plot_bitmaps()

    # Store local variables
    global local_vars
    local_vars = inspect.currentframe().f_locals


# Run if main file
if __name__ == "__main__":
    main()
