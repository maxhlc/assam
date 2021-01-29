#!/usr/bin/env python

import gmatInterface


def propagate(start_time, end_time, keplerian_elements, propagator="gmat"):
    """
    Function to handle propagators for satellite frame generation.

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

    Raises
    ------
    ValueError
        Error if specified propagator option is not available.

    Returns
    -------
    satellite_state : astropy.coordinates.builtin_frames.gcrs.GCRS
        Satellite state in the GCRS reference frame.
    satellite_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
        Satellite reference frame relative to the Earth's centre of mass
        with the same orientation as BCRS/ICRS.

    """

    # Select propagator
    if propagator == "gmat":
        # Create GMAT interface object
        gmat = gmatInterface.gmatInterface(
            start_time, end_time, keplerian_elements)
        # Propagate using GMAT
        gmat.generate_script()
        gmat.execute_script()
        # Load state
        satellite_state, satellite_frame = gmat.load_state()

    else:
        # Raise error if propagator not available
        raise ValueError("Invalid propagator")

    return satellite_state, satellite_frame
