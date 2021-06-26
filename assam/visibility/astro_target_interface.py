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
from astropy.coordinates import SkyCoord
import numpy as np
from tqdm import tqdm

from .astro_target import AstroTarget, AstroSubtarget


def load(spacecraft_frame, num_workers=None):
    """
    Function to import targets and their subtargets.

    Parameters
    ----------
    spacecraft_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
        Spacecraft reference frame relative to the Earth's geocentre
        with the same orientation as BCRS/ICRS.
    num_workers : int, optional
        Number of workers for multiprocessing.

    Raises
    ------
    ValueError
        Error if targets file is empty, or if subtarget shape is invalid.

    Returns
    -------
    targets : list
        Targets and their properties.

    """

    # Load targets from config file
    # TODO: implement default and optional paths
    with open("data/targets.yml", "r") as targets_file:
        targets_dump = yaml.safe_load(targets_file)

    # Check for empty targets file
    if targets_dump is None:
        raise ValueError("Empty target file")

    # Create list of worker parameters
    worker_params = [(target_dump, spacecraft_frame)
                     for target_dump in targets_dump.items()]

    # Generate target objects
    # TODO: value checking
    targets = []
    # Create worker pool
    with multiprocessing.Pool(num_workers) as p:
        # Create progress bar
        with tqdm(total=len(targets_dump), desc="Target Generation") as pbar:
            # Iterate through targets
            for target in p.imap(load_worker, worker_params):
                # Store in target list
                targets.append(target)

                # Update progress bar
                pbar.update()

    return targets


def load_worker(worker_params):
    """
    Worker function for loading targets.

    Parameters
    ----------
    worker_params : tuple
        Parameters for the worker including target information and the
        spacecraft frame.

    Raises
    ------
    ValueError
        Error if the subtarget shape is invalid.

    Returns
    -------
    target : AstroTarget
        Target object containing its properties.

    """

    # Extract worker params
    target_dump, spacecraft_frame = worker_params

    # Extract target name and info
    target_name, target_info = target_dump

    # Extract general properties
    target_priority = target_info["priority"]
    target_category = target_info["category"]

    # Create empty target with general properties
    target = AstroTarget(target_name, target_priority, target_category)

    # Generate subtargets and add to target object
    for subtarget_name, subtarget_info in target_info["subtargets"].items():
        # Import frame and coordinates
        frame = subtarget_info["frame"]
        centre = subtarget_info["centre"] * u.deg
        original_coordinates = SkyCoord(centre[0], centre[1], frame=frame)

        # Convert into ICRF and satellite frame
        icrs_coordinates = original_coordinates.transform_to("icrs")
        coordinates = original_coordinates.transform_to(spacecraft_frame)

        # Calculate subtarget geometry
        shape = subtarget_info["shape"]
        if shape == "rectangular":
            # Assign width and height
            width = subtarget_info["width"] * u.deg
            height = subtarget_info["height"] * u.deg
            # Calculate bounding circle angular radius
            angular_radius = 0.5*np.sqrt(width**2 + height**2)
        elif shape == "circular":
            # Assign nan width and height
            width = np.nan
            height = np.nan
            # Assign angular
            angular_radius = subtarget_info["angular_radius"] * u.deg
        else:
            raise ValueError(f"Invalid subtarget shape: {target_name}, {subtarget_name}")

        # Create subtarget object
        subtarget = AstroSubtarget(subtarget_name,
                                   frame,
                                   centre,
                                   shape,
                                   width, height,
                                   angular_radius,
                                   coordinates,
                                   icrs_coordinates)

        # Add subtarget to target object
        target.add_subtarget(subtarget)

    return target


def save():
    # TODO: implement method to save targets to file
    pass
