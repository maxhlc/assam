#!/usr/bin/env python

from astropy.coordinates import solar_system_ephemeris, get_body


class visiblityModule():
    
    def __init__(self,satellite_frame):
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

        # Get coordinates for solar system bodies in the satellite frame 
        # at the satellite frame observation times and store in a dictionary
        bodies_coord = {}
        for body in bodies:
            body_coord = get_body(body, self.satellite_frame.obstime)
            bodies_coord[body] = body_coord.transform_to(self.satellite_frame)

        # Store output            
        self.bodies_coord = bodies_coord

        return bodies_coord

    def get_targets(self):
        pass
        return None

    def calculate_separation(self):
        pass
        return None
