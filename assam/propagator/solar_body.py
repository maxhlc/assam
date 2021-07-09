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

class SolarBody():

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
