#!/usr/bin/env python

from gmatInterface import gmatInterface
import solarBodyInterface


class propagatorModule():

    def __init__(self, start_time, end_time, keplerian_elements, propagator="gmat"):
        """
        Initialisation function for propagator module.

        Parameters
        ----------
        start_time : astropy.time.core.Time
            Mission start time.
        end_time : astropy.time.core.Time
            Mission end time.
        keplerian_elements : dict
            Earth-centered Keplerian elements of the satellite.
        propagator : str, optional
            Propagator option. The default is "gmat".

        Returns
        -------
        None.

        """

        # Load parameters
        self.start_time = start_time
        self.end_time = end_time
        self.keplerian_elements = keplerian_elements
        self.propagator = propagator

    def propagate_spacecraft(self):
        """
        Function to handle propagators for satellite frame generation.

        Raises
        ------
        ValueError
            Error if specified propagator option is not available.

        Returns
        -------
        spacecraft_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
            Spacecraft reference frame relative to the Earth's centre of mass
            with the same orientation as BCRS/ICRS.

        """

        # Propagate spacecraft
        if self.propagator == "gmat":
            # Run orbit propagation
            gmat = gmatInterface(self.start_time,
                                 self.end_time,
                                 self.keplerian_elements)
            gmat.generate_script()
            gmat.execute_script()
            gmat.load_state()

            # Extract satellite frame
            spacecraft_frame = gmat.satellite_frame
        else:
            # Raise error if propagator not available
            raise ValueError("Invalid propagator")

        # Store satellite frame
        self.spacecraft_frame = spacecraft_frame

        return spacecraft_frame

    def get_solar_bodies(self):
        """
        Function to get the import solar bodies.

        Returns
        -------
        solar_bodies : list
            Solar system bodies and their properties.

        """

        # Load solar bodies
        solar_bodies = solarBodyInterface.load(self.spacecraft_frame)

        # Store output
        self.solar_bodies = solar_bodies

        return solar_bodies
