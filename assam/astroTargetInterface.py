#!/usr/bin/env python

from astropy.coordinates import SkyCoord
from astropy import units as u
import yaml
import numpy as np
from tqdm import tqdm

from astroTarget import astroTarget, astroSubtarget


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
        target = astroTarget(target_name, target_priority, target_category)

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
            subtarget = astroSubtarget(subtarget_name,
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
