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

import numpy as np
import pandas as pd
from astropy import units as u


def rle(inarray):
    """
    Function to convert arrays to run-length encoding scheme, as found at:
        https://stackoverflow.com/a/32681075

    Parameters
    ----------
    inarray
        Array of values.

    Returns
    -------
    np.ndarray
        Array of lengths.
    np.ndarray
        Array of start indicies.
    np.ndarray
        Array of run values.

    """

    ia = np.asarray(inarray)                # force numpy
    n = len(ia)
    if n == 0:
        return (None, None, None)
    else:
        y = ia[1:] != ia[:-1]               # pairwise unequal (string safe)
        i = np.append(np.where(y), n - 1)   # must include last element posi
        z = np.diff(np.append(-1, i))       # run lengths
        p = np.cumsum(np.append(0, z))[:-1]  # positions
        return(z, p, ia[i])


class AstroTarget():

    def __init__(self, name, priority, category):
        """
        Initialisation function for astronomical targets.

        Parameters
        ----------
        name : str
            Name of the target.
        priority : int
            Priority of the target.
        category : str
            Category of the target.

        Returns
        -------
        None.

        """

        # Load target properties
        self.name = name
        self.priority = priority
        self.category = category

        # Create empty list for subtargets
        self.subtargets = []

    def add_subtarget(self, subtarget):
        """
        Function to add subtarget to the target.

        Parameters
        ----------
        subtarget : astroSubtarget
            Subtarget object.

        Returns
        -------
        None.

        """

        # Add subtarget to dictionary
        self.subtargets.append(subtarget)

    def remove_subtarget(self, subtarget):
        """
        Function to remove subtarget from target.

        Parameters
        ----------
        subtarget : astroSubtarget
            Subtarget object.

        Returns
        -------
        None.

        """

        # Remove subtarget from target
        self.subtargets.remove(subtarget)

    def calculate_visibility(self, solar_bodies):
        """
        Function to calculate target visibility.

        Parameters
        ----------
        solar_bodies : list
            Solar system bodies and their properties.

        Returns
        -------
        visibility : numpy.ndarray
            Array of booleans, true when target is visible.

        """

        # TODO: implement storage of visibility per subtarget and solar body

        # Declare visibility list
        visibility = []

        # Store time vector
        # TODO: consider scenario of mismatching times between subtargets
        self.obstime = self.subtargets[0].coordinates.obstime

        # Iterate through subtargets and solar bodies to calculate visibility
        for subtarget in self.subtargets:
            for solar_body in solar_bodies:
                # Calculate visibility
                sub_visibility, _ = subtarget.calculate_visibility(solar_body)
                visibility.append(sub_visibility)

        # Convert visibility list to array
        visibility = np.array(visibility)

        # Flatten array into vector
        visibility = np.all(visibility, axis=0)

        # Store visibility
        self.visibility = visibility

        return visibility

    def calculate_contacts(self):
        # TODO: docstring

        # Calculate run-length encoding
        ilength, istart, ivalue = rle(self.visibility)

        # Calculate end index and clip
        iend = istart + ilength
        iend = np.clip(iend, 0, len(self.visibility)-1)

        # Remove runs where target is not visible, or if it starts at the end
        ix = np.where((ivalue == True) & (istart != len(self.visibility)-1))
        ilength = ilength[ix]
        istart = istart[ix]
        iend = iend[ix]

        # Calculate times
        start = self.obstime[istart]
        end = self.obstime[iend]

        # Create list of contacts
        contacts = [TargetContact(self, s, e, 1/self.priority, differential_benefit=True)
                    for s, e in zip(start, end)]

        # Store contacts
        self.contacts = contacts

        # Return contacts
        return contacts

    def calculate_overall_stats(self):
        # TODO: docstring
        # TODO: how to handle contact objects with verbose time?

        # Create empty statistics dictionary
        stats = dict()

        # Target name
        stats["name"] = self.name

        # Target category
        stats["category"] = self.category

        # Extract contact durations into list
        contact_durations = [contact.duration for contact in self.contacts]

        # Calculate number of contacts
        stats["n_contacts"] = len(contact_durations)
        
        # Check whether contacts occured
        if stats["n_contacts"] == 0:
            # Assign values if no contacts exist
            stats["total_duration"] = 0
            stats["mean_duration"] = np.nan
            stats["stddev_duration"] = np.nan
        else:
            # Calculate total contact duration
            stats["total_duration"] = np.sum(contact_durations)
    
            # Calculate mean contact duration
            stats["mean_duration"] = np.mean(contact_durations)
    
            # Calculate contact duration standard deviation
            stats["stddev_duration"] = np.std(contact_durations)

        # Convert statistics dictionary into DataFrame
        stats = pd.DataFrame([stats])

        # Store overall stats
        self.stats = stats

        return stats


class AstroSubtarget():

    def __init__(self, name, frame, centre, shape, width, height, angular_radius, coordinates):
        """
        Initialisation function for astronomical subtargets.

        Parameters
        ----------
        name : str
            Name of the subtarget.
        frame : str
            Subtarget reference frame.
        centre : astropy.units.quantity.Quantity
            Subtarget centre coordinates.
        shape : str
            Subtarget shape.
        width : astropy.units.quantity.Quantity
            Subtarget width.
        height : astropy.units.quantity.Quantity
            Subtarget height.
        angular_radius : astropy.units.quantity.Quantity
            Subtarget angular radius.
        coordinates : astropy.coordinates.sky_coordinate.SkyCoord
            Subtarget centre coordinates.

        Returns
        -------
        None.

        """

        # Load subtarget properties
        self.name = name
        self.frame = frame
        self.centre = centre
        self.shape = shape
        self.width = width
        self.height = height
        self.angular_radius = angular_radius
        self.coordinates = coordinates

    def calculate_visibility(self, solar_body):
        """
        Function to calculate subtarget visibility.

        Parameters
        ----------
        solar_body : solarBody
            Solar body object to calculate visibility.

        Returns
        -------
        visibility : numpy.ndarray
            Array of booleans, true when subtarget is visible.
        angular_separation : astropy.coordinates.angles.Angle
            Array of angular separation between subtarget and solar body.

        """

        # Declare visibility list
        visibility = []

        # Calculate angular separation
        angular_separation = solar_body.coordinates.separation(
            self.coordinates)

        # Calculate basic visibility
        visibility.append((angular_separation
                           - self.angular_radius
                           - solar_body.angular_radius) >= 0)

        # Calculate soft radius restrictions
        for radius_inner, radius_outer in solar_body.soft_radius:
            # Inner visibility (true if violating)
            visibility_inner = (angular_separation
                                + self.angular_radius
                                - radius_inner) > 0
            # Outer visibility (true if violating)
            visibility_outer = (angular_separation
                                - self.angular_radius
                                - radius_outer) < 0

            # Combine and invert, append to visibility list
            visibility_soft = np.logical_not(
                np.logical_and(visibility_inner, visibility_outer))
            visibility.append(visibility_soft)

        # Calculate arbitrary geometry
        # TODO: implement

        # Convert visibility list to array
        visibility = np.array(visibility)

        # Flatten array into vector
        visibility = np.all(visibility, axis=0)

        return visibility, angular_separation


class TargetContact():

    def __init__(self, target, start, end, benefit, differential_benefit=False, verbose_time=False):
        # TODO: docstring

        # Store target object
        self.target = target

        # Store start/end times and contact duration
        #
        # Verbose time stores the entire astropy.Time object, however this
        # requires high amounts of memory and significantly reduces
        # performance for following lookups and calculations
        #
        if verbose_time:
            # TODO: full implementation of verbose times
            raise(NotImplementedError)
            self.start = start
            self.end = end
        else:
            # TODO: consider use of astropy units to aid later calculations
            self.start = start.jd
            self.end = end.jd

        self.duration = self.end - self.start

        # Calculate benefit
        # TODO: benefit calculation when using verbose time
        if differential_benefit:
            self.benefit = benefit * self.duration
        else:
            self.benefit = benefit
