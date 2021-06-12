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

import yaml

from astropy import units as u
from astropy.coordinates import SkyCoord
import numpy as np
from tqdm import tqdm

from .astro_target import AstroTarget, AstroSubtarget


def load(satellite_frame):
    """
    Function to import targets and their subtargets.

    Parameters
    ----------
    satellite_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
        Satellite reference frame relative to the Earth's centre of mass
        with the same orientation as BCRS/ICRS.

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
    with open("../data/targets.yml", "r") as targets_file:
        targets_dump = yaml.safe_load(targets_file)

    # Check for empty targets file
    if targets_dump is None:
        raise ValueError("Empty target file")

    # Generate target objects
    # TODO: value checking
    targets = []
    for target_name, target_info in tqdm(targets_dump.items(), desc="Target Generation"):
        # Extract general properties
        target_priority = target_info["priority"]
        target_category = target_info["category"]

        # Create empty target with general properties
        target = AstroTarget(target_name, target_priority, target_category)

        # Generate subtargets and add to target object
        for subtarget_name, subtarget_info in target_info["subtargets"].items():
            # Create astropy state
            frame = subtarget_info["frame"]
            centre = subtarget_info["centre"] * u.deg
            coordinates = SkyCoord(centre[0], centre[1], frame=frame)
            coordinates = coordinates.transform_to(satellite_frame)

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
                raise ValueError(
                    f"Invalid subtarget shape: {target_name}, {subtarget_name}")

            # Create subtarget object
            subtarget = AstroSubtarget(subtarget_name,
                                       frame,
                                       centre,
                                       shape,
                                       width, height,
                                       angular_radius,
                                       coordinates)

            # Add subtarget to target object
            target.add_subtarget(subtarget)

        # Store in target list
        targets.append(target)

    return targets


def save():
    # TODO: implement method to save targets to file
    pass
