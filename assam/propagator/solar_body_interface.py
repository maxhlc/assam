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
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import multiprocessing
import yaml

from astropy import units as u
from astropy.coordinates import solar_system_ephemeris, get_body
import numpy as np
from tqdm import tqdm

from .solar_body import SolarBody


def load(spacecraft_frame, ephem="jpl", num_workers=None):
    """
    Function to get the coordinates of solar bodies.

    Parameters
    ----------
    spacecraft_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
        Spacecraft reference frame relative to the Earth's centre of mass
        with the same orientation as BCRS/ICRS.
    ephem : str, optional
        Ephemeris selection.
    num_workers : int, optional
        Number of workers for multiprocessing.

    Raises
    ------
    ValueError
        Error if solar bodies file is empty.

    Returns
    -------
    solar_bodies : list
        Solar system bodies and their properties.

    """

    # Set ephemeris data
    solar_system_ephemeris.set(ephem)

    # Load solar bodies of interest from config
    # TODO: implement default and optional paths
    with open("data/solar_bodies.yml", "r") as solar_bodies_file:
        solar_bodies_dump = yaml.safe_load(solar_bodies_file)

    # Check for empty solar bodies file
    if solar_bodies_dump is None:
        raise ValueError("Empty solar bodies file")

    # Create list of included solar bodies to supply to multiprocessing
    solar_bodies_list = [(solar_body_name, solar_body_info, spacecraft_frame)
                         for solar_body_name, solar_body_info
                         in solar_bodies_dump.items()
                         if solar_body_info["included"]]

    # Generate solar body objects
    # TODO: value checking
    solar_bodies = []
    # Create worker pool
    with multiprocessing.Pool(num_workers) as p:
        # Create progress bar
        with tqdm(total=len(solar_bodies_list), desc="Solar Body Generation") as pbar:
            # Iterate through solar bodies
            for solar_body_object in p.imap(load_worker, solar_bodies_list):
                # Add solar body object to list
                solar_bodies.append(solar_body_object)
                
                # Update progress bar
                pbar.update()

    return solar_bodies


def load_worker(worker_params):
    """
    Worker function for loading solar bodies.

    Parameters
    ----------
    worker_params : tuple
        Parameters for the worker, including the solar body name,
        solar body information, and satellite reference frame.

    Returns
    -------
    solar_body_object : solarBody
        Solar body object.

    """

    # Unpack worker parameter tuple
    solar_body_name, solar_body_info, spacecraft_frame = worker_params

    # Calculate solar body coordinates from ephemeris data
    solar_body_coords = get_body(solar_body_name, spacecraft_frame.obstime)

    # Convert to spacecraft frame coordinates
    solar_body_coords = solar_body_coords.transform_to(spacecraft_frame)

    # Find slant range between satellite and solar body
    slant_range = solar_body_coords.distance

    # Calculate solar body angular radius
    solar_body_radius = solar_body_info["radius"] * u.m
    solar_body_angular_radius = np.arcsin(solar_body_radius / slant_range)

    # Load soft radius constraints
    solar_body_soft_radius = solar_body_info["soft_radius"] * u.deg

    # Create solar body object
    solar_body_object = SolarBody(solar_body_name,
                                  solar_body_coords,
                                  solar_body_radius,
                                  solar_body_angular_radius,
                                  solar_body_soft_radius)

    return solar_body_object
