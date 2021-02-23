#!/usr/bin/env python

from tqdm import tqdm

import solarBodyInterface
import astroTargetInterface


class visibilityModule():

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

    def get_solar_bodies(self):
        """
        Function to get the import solar bodies.

        Returns
        -------
        solar_bodies : dict
            Solar system bodies and their properties.

        """

        # Load solar bodies
        solar_bodies = solarBodyInterface.load(self.satellite_frame)

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
        targets = astroTargetInterface.load(self.satellite_frame)

        # Store output
        self.targets = targets

        return targets

    def calculate_visibility(self):
        """
        Function to calculate target visibility.

        Returns
        -------
        None.

        """

        # Iterate through targets to calculate visibility
        for target in tqdm(self.targets, desc="Target Visibility"):
            target.calculate_visibility(self.solar_bodies)
