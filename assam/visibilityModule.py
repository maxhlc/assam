#!/usr/bin/env python

from solarBodyInterface import solarBodyInterface
from astroTargetInterface import astroTargetInterface

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
        Function to get the import solar bodies.

        Returns
        -------
        solar_bodies : dict
            Solar system bodies and their properties.

        """
        
        # Load solar bodies
        solar_bodies = solarBodyInterface.load(self.satellite_state,
                                               self.satellite_frame)

        # Store output
        self.solar_bodies = solar_bodies

        return solar_bodies

    def get_targets(self):
        """
        Function to import targets.

        Returns
        -------
        targets : dict
            Targets and their properties.

        """
        
        # Load targets
        targets = astroTargetInterface.load()

        # Store output
        self.targets = targets

        return targets

    def calculate_separation(self):
        pass
        return None
