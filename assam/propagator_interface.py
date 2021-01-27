#!/usr/bin/env python

import numpy as np
from astropy.coordinates import GCRS
import gmat_interface

def propagate(start_time,end_time,keplerian_elements,propagator="gmat"):
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
    satellite_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
        Satellite reference frame relative to the Earth's centre of mass
        with the same orientation as BCRS/ICRS.

    """
    
    # Select propagator
    if propagator == "gmat":
        # Propagate using GMAT
        satellite_state_table = gmat_interface.run_gmat(start_time, end_time,
                                          keplerian_elements)
        
        # Extract satellite state
        satellite_obstime = satellite_state_table["JD"]  
        X = np.reshape(satellite_state_table["X"],(1,-1))
        Y = np.reshape(satellite_state_table["Y"],(1,-1))
        Z = np.reshape(satellite_state_table["Z"],(1,-1))       
        VX = np.reshape(satellite_state_table["VX"],(1,-1))
        VY = np.reshape(satellite_state_table["VY"],(1,-1))
        VZ = np.reshape(satellite_state_table["VZ"],(1,-1))
        
        # Convert satellite state to required observer format
        satellite_obsgeoloc = np.concatenate((X, Y, Z),axis=0)
        satellite_obsgeovel = np.concatenate((VX, VY, VZ),axis=0)
        
        # Generate satellite reference frame assuming that the EarthMJ2000Eq
        # reference frame is equivalent to GCRS
        satellite_frame = GCRS(representation_type="cartesian",
                               obstime=satellite_obstime,
                               obsgeoloc=satellite_obsgeoloc,
                               obsgeovel=satellite_obsgeovel)
        
    else:
        # Raise error if propagator not available
        raise ValueError("Invalid propagator")
    
    return satellite_frame