#!/usr/bin/env python

import numpy as np


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
        contacts = [TargetContact(self, s, e) for s, e in zip(start, end)]
        
        # Store contacts
        self.contacts = contacts
        
        # Return contacts
        return contacts


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

    def __init__(self, target, start, end):
        # TODO: docstring

        # Store target and target priority
        self.target = target
        self.priority = target.priority
        
        self.benefit = 1/self.priority

        # Store start/end times and contact duration
        # TODO: address memory issues when using full time object
        self.start = start
        self.end = end
        self.duration = end - start
