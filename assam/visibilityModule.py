#!/usr/bin/env python

from astropy.coordinates import solar_system_ephemeris, get_body
from astropy import units as u
import yaml
import numpy as np


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
        solar_bodies = {}
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

            # Store solar body objects
            solar_bodies[solar_body] = solarBody(solar_body,
                                                 solar_body_coords,
                                                 solar_body_radius,
                                                 solar_body_angular_radius)

        # Store output
        self.solar_bodies = solar_bodies

        return solar_bodies

    def get_targets(self):
        pass
        return None

    def calculate_separation(self):
        pass
        return None


class solarBody():

    def __init__(self, name, coordinates, radius, angular_radius):
        """
        Initialisation function for solar body objects.

        Parameters
        ----------
        name : str
            Solar body name.
        coordinates : astropy.coordinates.sky_coordinate.SkyCoord
            Solar body coordinates in the satellite frame.
        radius : astropy.units.quantity.Quantity
            Solar body radius.
        angular_radius : astropy.units.quantity.Quantity
            Solar body angular radius from the viewpoint of the satellite.

        Returns
        -------
        None.

        """

        # Load body properties
        self.name = name
        self.coordinates = coordinates
        self.radius = radius
        self.angular_radius = angular_radius

        return None


class astroTarget():

    def __init__(self, target_name, target_priority, target_category):
        """
        Initialisation function for astronomical targets

        Parameters
        ----------
        target_name : str
            Name of the target.
        target_priority : int
            Priority of the target.
        target_category : str
            Category of the target.

        Returns
        -------
        None.

        """
        
        # Load target properties
        self.target_name = target_name
        self.target_priority = target_priority
        self.target_category = target_category
        
        # Create empty dictionary for subtargets
        self.subtargets = {}

        return None

    def add_subtarget(self, subtarget_name, subtarget):
        """
        Function to add subtarget to the target.

        Parameters
        ----------
        subtarget_name : str
            Name of the subtarget.
        subtarget : astroSubtarget
            Subtarget object.

        Returns
        -------
        None.

        """

        # Add subtarget to dictionary
        self.subtargets[subtarget_name] = subtarget

        return None

    def remove_subtarget(self, subtarget_name):
        """
        Function to remove subtarget from target.

        Parameters
        ----------
        subtarget_name : str
            Name of the subtarget.

        Returns
        -------
        None.

        """        

        # Remove subtarget from target
        self.subtargets.pop(subtarget_name)

        return None


class astroSubtarget():

    def __init__(self):
        pass
        return None
