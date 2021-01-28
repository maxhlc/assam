#!/usr/bin/env python

from astropy.time import Time

import propagator
import visibility

# Set parameters
start_time = Time("2021-01-23 12:30")
end_time = Time("2021-01-23 13:30")
keplerian_elements = {"SMA": 7000,
                      "ECC": 0,
                      "INC": 98.6,
                      "RAAN": 0,
                      "AOP": 0,
                      "TA": 0}

# Run orbit propagation
satellite_state, satellite_frame = propagator.propagate(
    start_time, end_time, keplerian_elements)

# Calculate target visibility
visibility.visible(satellite_frame)