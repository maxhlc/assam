#!/usr/bin/env python

class solarBody():

    def __init__(self, name, coordinates, radius, angular_radius, soft_radius):
        """
        Initialisation function for solar body objects.

        Parameters
        ----------
        name : str
            Solar body name.
        coordinates : astropy.coordinates.sky_coordinate.SkyCoord
            Solar body coordinates in the satellite frame.
        radius : astropy.units.quantity.Quantity
            Solar body radius.
        angular_radius : astropy.units.quantity.Quantity
            Solar body angular radius from the viewpoint of the satellite.
        soft_radius : astropy.units.quantity.Quantity
            Solar body soft radius constraint.

        Returns
        -------
        None.

        """

        # Load body properties
        self.name = name
        self.coordinates = coordinates
        self.radius = radius
        self.angular_radius = angular_radius
        self.soft_radius = soft_radius

        return None
