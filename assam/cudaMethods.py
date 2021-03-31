#!/usr/bin/env python

import numpy as np
import cupy as cp
from astropy import units as u


def separation_cuda(coord1, coord2):
    # TODO: docstring

    # TODO: check equivalent reference frames

    # Extract angles
    lon1 = coord1.spherical.lon
    lat1 = coord1.spherical.lat
    lon2 = coord2.spherical.lon
    lat2 = coord2.spherical.lat

    # Convert to cupy arrays in radians
    lon1 = cp.array(lon1.rad)
    lat1 = cp.array(lat1.rad)
    lon2 = cp.array(lon2.rad)
    lat2 = cp.array(lat2.rad)

    # Calculate angle using Vincenty formula,
    # as used by astropy angle utilities
    sdlon = cp.sin(lon2 - lon1)
    cdlon = cp.cos(lon2 - lon1)
    slat1 = cp.sin(lat1)
    slat2 = cp.sin(lat2)
    clat1 = cp.cos(lat1)
    clat2 = cp.cos(lat2)
    num1 = clat2 * sdlon
    num2 = clat1 * slat2 - slat1 * clat2 * cdlon
    denominator = slat1 * slat2 + clat1 * clat2 * cdlon
    angle = cp.arctan2(np.hypot(num1, num2), denominator)

    # Convert angle to numpy array with astropy units
    angle = cp.asnumpy(angle) * u.rad

    return angle
