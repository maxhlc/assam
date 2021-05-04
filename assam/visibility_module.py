#!/usr/bin/env python

import pandas as pd
from tqdm import tqdm

import astro_target_interface


class VisibilityModule():

    def __init__(self, spacecraft_frame, solar_bodies):
        """
        Initialisation function for the visibility module.

        Parameters
        ----------
        spacecraft_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
            Spacecraft reference frame relative to the Earth's centre of mass
            with the same orientation as BCRS/ICRS.
        solar_bodies : list
            Solar system bodies and their properties.

        Returns
        -------
        None.

        """

        # Load satellite reference frame and solar bodies
        self.spacecraft_frame = spacecraft_frame
        self.solar_bodies = solar_bodies

    def get_targets(self):
        """
        Function to import targets.

        Returns
        -------
        targets : list
            Targets and their properties.

        """

        # Load targets
        targets = astro_target_interface.load(self.spacecraft_frame)

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
            
    def calculate_contacts(self):
        # TODO: docstring
        
        # Iterate through targets to calculate contacts
        for target in tqdm(self.targets, desc="Target Contacts"):
            target.calculate_contacts()
            
    def calculate_overall_stats(self):
        # TODO: docstring
        
        # Declare overall statistics list
        stats = []
        
        # Iterate through targets to calculate overall stats
        for target in tqdm(self.targets, desc="Target Overall Statistics"):
            target_stats = target.calculate_overall_stats()
            stats.append(target_stats)
            
        # Convert statistics list into DataFrame
        stats = pd.concat(stats, ignore_index=True)
        
        # Store statistics
        self.stats = stats
        
        return stats
        
