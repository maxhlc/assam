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
        
        # Declare empty variables
        self.targets = None
        self.stats = None

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
        """
        Function to calculate target contacts.

        Returns
        -------
        None.

        """

        # Iterate through targets to calculate contacts
        for target in tqdm(self.targets, desc="Target Contacts"):
            target.calculate_contacts()

    def calculate_overall_stats(self):
        """
        Function to calculate target statistics.

        Returns
        -------
        stats : pandas.core.frame.DataFrame
            Overall statistics of target contacts.

        """

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
