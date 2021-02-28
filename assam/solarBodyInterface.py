#!/usr/bin/env python

import multiprocessing
from astropy.coordinates import solar_system_ephemeris, get_body
from astropy import units as u
import yaml
import numpy as np
from tqdm import tqdm

from solarBody import solarBody


def load(satellite_frame, ephem="jpl", num_workers=None):
    """
    Function to get the coordinates of solar bodies.

    Parameters
    ----------
    satellite_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
        Satellite reference frame relative to the Earth's centre of mass
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
    with open("../data/solar_bodies.yml", "r") as solar_bodies_file:
        solar_bodies_dump = yaml.safe_load(solar_bodies_file)

    # Check for empty solar bodies file
    if solar_bodies_dump is None:
        raise ValueError("Empty solar bodies file")

    # Create list of included solar bodies to supply to multiprocessing
    solar_bodies_list = [(solar_body_name, solar_body_info, satellite_frame)
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
    solar_body_name, solar_body_info, satellite_frame = worker_params

    # Calculate solar body coordinates from ephemeris data
    solar_body_coords = get_body(solar_body_name, satellite_frame.obstime)

    # Convert to satellite frame coordinates
    solar_body_coords = solar_body_coords.transform_to(satellite_frame)

    # Find slant range between satellite and solar body
    slant_range = solar_body_coords.distance

    # Calculate solar body angular radius
    # TODO: implement more accurate calculation for close bodies
    #       such as the Earth
    solar_body_radius = solar_body_info["radius"] * u.m
    solar_body_angular_radius = np.arcsin(
        solar_body_radius / slant_range)

    # Load soft radius constraints
    solar_body_soft_radius = solar_body_info["soft_radius"] * u.deg

    # Create solar body object
    solar_body_object = solarBody(solar_body_name,
                                  solar_body_coords,
                                  solar_body_radius,
                                  solar_body_angular_radius,
                                  solar_body_soft_radius)

    return solar_body_object
