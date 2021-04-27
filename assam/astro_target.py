#!/usr/bin/env python

import numpy as np


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
