#!/usr/bin/env python

import propagator_interface
from astropy.time import Time

# Set parameters
start_time = Time("2021-01-23 12:30")
end_time = Time("2021-01-24 12:30")
keplerian_elements = {"SMA": 7000,
                      "ECC": 0,
                      "INC": 98.6,
                      "RAAN": 0,
                      "AOP": 0,
                      "TA": 0}

# Run orbit propagation
satellite_state, satellite_frame = propagator_interface.propagate(
    start_time, end_time,keplerian_elements)