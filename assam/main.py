#!/usr/bin/env python

import propagator_interface
from astropy.time import Time

# Set parameters
start_time = Time("2021-01-23 12:33")
end_time = Time("2021-01-24 13:33")
keplerian_elements = {"SMA": 8000,
                      "ECC": 0.01,
                      "INC": 45,
                      "RAAN": 0,
                      "AOP": 0,
                      "TA": 0}

# Run orbit propagation
satellite_frame = propagator_interface.propagate(start_time, end_time,
                                                 keplerian_elements)