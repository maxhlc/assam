#!/usr/bin/env python

class astroTarget():

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

        # Create empty dictionary for subtargets
        self.subtargets = dict()

        return None

    def add_subtarget(self, subtarget_name, subtarget):
        """
        Function to add subtarget to the target.

        Parameters
        ----------
        subtarget_name : str
            Name of the subtarget.
        subtarget : astroSubtarget
            Subtarget object.

        Returns
        -------
        None.

        """

        # Add subtarget to dictionary
        self.subtargets[subtarget_name] = subtarget

        return None

    def remove_subtarget(self, subtarget_name):
        """
        Function to remove subtarget from target.

        Parameters
        ----------
        subtarget_name : str
            Name of the subtarget.

        Returns
        -------
        None.

        """

        # Remove subtarget from target
        self.subtargets.pop(subtarget_name)

        return None


class astroSubtarget():

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

        return None
