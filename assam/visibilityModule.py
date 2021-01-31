#!/usr/bin/env python

from astropy.coordinates import solar_system_ephemeris, get_body
import yaml


class visiblityModule():

    def __init__(self, satellite_frame):
        """
        Initialisation function for the visibility module.

        Parameters
        ----------
        satellite_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
            Satellite reference frame relative to the Earth's centre of mass
            with the same orientation as BCRS/ICRS.

        Returns
        -------
        None.

        """

        # Load satellite reference frame
        self.satellite_frame = satellite_frame

        return None

    def get_solar_bodies(self):
        """
        Function to get the coordinates of solar bodies.

        Returns
        -------
        bodies_coord : dict
            Solar system bodies and their coordinates in the satellite frame.

        """

        # Attempt to use JPL ephemeris data (requires jplephem package),
        # if not use the default ephemeris data
        try:
            solar_system_ephemeris.set("jpl")
        except:
            solar_system_ephemeris.set("builtin")

        # Set solar bodies of interest
        with open("../data/solar_bodies.yml", "r") as solar_bodies_file:
            solar_bodies = yaml.safe_load(solar_bodies_file)

        # Get coordinates for solar system bodies in the satellite frame
        solar_bodies_coords = {}
        for solar_body, solar_body_info in solar_bodies.items():
            # Continue to following solar body if current one not included
            if not solar_body_info["included"]:
                continue

            # Calculate solar body coordinates from ephemeris data
            solar_body_coords = get_body(solar_body,
                                         self.satellite_frame.obstime)
            # Store solar bodies coordinates in the satellite frame
            solar_bodies_coords[solar_body] = solar_body_coords.transform_to(
                self.satellite_frame)

        # Store output
        self.solar_bodies_coords = solar_bodies_coords

        return solar_bodies_coords

    def get_targets(self):
        pass
        return None

    def calculate_separation(self):
        pass
        return None
