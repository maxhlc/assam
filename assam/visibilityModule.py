#!/usr/bin/env python

from astropy.coordinates import solar_system_ephemeris, get_body, SkyCoord
from astropy import units as u
import yaml
import numpy as np

from astroTarget import astroTarget, astroSubtarget
from solarBody import solarBody


class visibilityModule():

    def __init__(self, satellite_state, satellite_frame):
        """
        Initialisation function for the visibility module.

        Parameters
        ----------
        satellite_state : astropy.coordinates.builtin_frames.gcrs.GCRS
            Satellite state in the GCRS reference frame.       
        satellite_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
            Satellite reference frame relative to the Earth's centre of mass
            with the same orientation as BCRS/ICRS.

        Returns
        -------
        None.

        """

        # Load satellite reference frame
        self.satellite_state = satellite_state
        self.satellite_frame = satellite_frame

        return None

    def get_solar_bodies(self):
        """
        Function to get the coordinates of solar bodies.

        Returns
        -------
        solar_bodies : dict
            Solar system bodies and their properties.

        """

        # Attempt to use JPL ephemeris data (requires jplephem package),
        # if not use the default ephemeris data
        try:
            solar_system_ephemeris.set("jpl")
        except:
            solar_system_ephemeris.set("builtin")

        # Load solar bodies of interest from config file
        with open("../data/solar_bodies.yml", "r") as solar_bodies_file:
            solar_bodies_dump = yaml.safe_load(solar_bodies_file)

        # Generate solar body objects
        # TODO: value checking
        solar_bodies = dict()
        for solar_body, solar_body_info in solar_bodies_dump.items():
            # Continue to following solar body if current one not included
            if not solar_body_info["included"]:
                continue

            # Calculate solar body coordinates from ephemeris data
            solar_body_coords = get_body(solar_body,
                                         self.satellite_frame.obstime)

            # Convert to satellite frame coordinates
            solar_body_coords = solar_body_coords.transform_to(
                self.satellite_frame)

            # Find slant range between satellite and solar body
            slant_range = solar_body_coords.separation_3d(self.satellite_state)

            # Calculate solar body angular radius
            # TODO: implement more accurate calculation for close bodies
            #       such as the Earth
            solar_body_radius = solar_body_info["radius"] * u.m
            solar_body_angular_radius = np.arctan(
                solar_body_radius / slant_range)

            # Load soft radius constraints
            solar_body_soft_radius = solar_body_info["soft_radius"] * u.deg

            # Create solar body object and store in dictionary
            solar_bodies[solar_body] = solarBody(solar_body,
                                                 solar_body_coords,
                                                 solar_body_radius,
                                                 solar_body_angular_radius,
                                                 solar_body_soft_radius)

        # Store output
        self.solar_bodies = solar_bodies

        return solar_bodies

    def get_targets(self):

        # Load targets from config file
        with open("../data/targets.yml", "r") as targets_file:
            targets_dump = yaml.safe_load(targets_file)
        
        # Check for empty targets file
        if targets_dump is None:
            raise ValueError("Empty target file")

        targets = dict()
        # Generate target objects
        # TODO: value checking
        for target_name, target_info in targets_dump.items():
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
                
                # Calculate subtarget geometry
                shape = subtarget_info["shape"]
                if  shape == "rectangular":
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
                subtarget = astroSubtarget(subtarget_name,
                                           frame,
                                           centre,
                                           shape,
                                           width, height,
                                           angular_radius,
                                           coordinates)
                
                # Add subtarget to target object
                target.add_subtarget(subtarget_name, subtarget)

            # Store in target dictionary
            targets[target_name] = target

        # Store output
        self.targets = targets

        return targets

    def calculate_separation(self):
        pass
        return None
