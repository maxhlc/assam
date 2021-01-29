#!/usr/bin/env python

from astropy.coordinates import solar_system_ephemeris, get_body


class visiblityModule():
    
    def __init__(self,satellite_frame):
        
        self.satellite_frame = satellite_frame
        
        pass
        return None

    def get_solar_bodies(self):
        """
        Function to get the coordinates of solar bodies.

        Returns
        -------
        bodies_coord : dict
            Solar bodies and their coordinates in GCRS.

        """

        # Attempt to use JPL ephemeris data (requires jplephem package),
        # if not use the default ephemeris data
        try:
            solar_system_ephemeris.set("jpl")
        except:
            solar_system_ephemeris.set("builtin")

        # Set solar bodies of interest
        # TODO: implement selection of which solar bodies to include
        bodies = [
            "sun",
            "mercury",
            "venus",
            "earth",
            "mars",
            "moon",
            "jupiter",
            "saturn",
            "uranus",
            "neptune"
        ]

        # Get coordinates for solar system bodies
        bodies_coord = {}
        for body in bodies:
            bodies_coord[body] = get_body(body, self.satellite_frame.obstime)

        return bodies_coord

    def get_targets(self):
        pass
        return None

    def calculate_separation(self):
        pass
        return None
