#!/usr/bin/env python

class astroTarget():

    def __init__(self, target_name, target_priority, target_category):
        """
        Initialisation function for astronomical targets.

        Parameters
        ----------
        target_name : str
            Name of the target.
        target_priority : int
            Priority of the target.
        target_category : str
            Category of the target.

        Returns
        -------
        None.

        """

        # Load target properties
        self.target_name = target_name
        self.target_priority = target_priority
        self.target_category = target_category

        # Create empty dictionary for subtargets
        self.subtargets = {}

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

    def __init__(self):
        pass
        return None
