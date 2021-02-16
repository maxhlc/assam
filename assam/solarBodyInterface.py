#!/usr/bin/env python

from astropy.coordinates import solar_system_ephemeris, get_body
from astropy import units as u
import yaml
import numpy as np
from tqdm import tqdm

from solarBody import solarBody

def load(satellite_frame, ephem="jpl"):
    """
    Function to get the coordinates of solar bodies.

    Parameters
    ----------
    satellite_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
        Satellite reference frame relative to the Earth's centre of mass
        with the same orientation as BCRS/ICRS.
    ephem : str, optional
        Ephemeris selection.

    Raises
    ------
    ValueError
        Error if solar bodies file is empty.

    Returns
    -------
    solar_bodies : dict
        Solar system bodies and their properties.

    """

    # Set ephemeris data
    solar_system_ephemeris.set(ephem)

    # Load solar bodies of interest from config
    # TODO: implement default and optional paths
    with open("../data/solar_bodies.yml", "r") as solar_bodies_file:
        solar_bodies_dump = yaml.safe_load(solar_bodies_file)

    # Check for empty solar bodies file
    if solar_bodies_dump is None:
        raise ValueError("Empty solar bodies file")

    # Generate solar body objects
    # TODO: value checking, parallel processing
    solar_bodies = []
    for solar_body, solar_body_info in tqdm(solar_bodies_dump.items(), desc="Solar Body Generation"):
        # Continue to following solar body if current one not included
        if not solar_body_info["included"]:
            continue

        # Calculate solar body coordinates from ephemeris data
        solar_body_coords = get_body(solar_body, satellite_frame.obstime)

        # Convert to satellite frame coordinates
        solar_body_coords = solar_body_coords.transform_to(satellite_frame)

        # Find slant range between satellite and solar body
        slant_range = solar_body_coords.distance

        # Calculate solar body angular radius
        # TODO: implement more accurate calculation for close bodies
        #       such as the Earth
        solar_body_radius = solar_body_info["radius"] * u.m
        solar_body_angular_radius = np.arctan(
            solar_body_radius / slant_range)

        # Load soft radius constraints
        solar_body_soft_radius = solar_body_info["soft_radius"] * u.deg

        # Create solar body object and store in dictionary
        solar_bodies.append(solarBody(solar_body,
                                      solar_body_coords,
                                      solar_body_radius,
                                      solar_body_angular_radius,
                                      solar_body_soft_radius))

    return solar_bodies
