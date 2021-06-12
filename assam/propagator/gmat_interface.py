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

import os

from astropy import units as u
from astropy.coordinates import GCRS, CartesianRepresentation
from astropy.time import Time
import numpy as np
import pandas as pd
from tqdm import tqdm

# Define paths for GMAT
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_PATH = os.path.join(DIR_PATH, "GMAT", "GMAT_template.script")
MODIFIED_PATH = os.path.join(DIR_PATH, "GMAT", "GMAT_modified.script")
OUTPUT_PATH = os.path.join(DIR_PATH, "GMAT", "GMAT_output.dat")

# Define offset for Modified Julian Dates
# (GMAT uses a non-standard offset, relative to 05 Jan 1941 12:00:00.000)
GMAT_MJD_OFFSET = 2430000.0


class GMATInterface():

    def __init__(self, start_time, end_time, time_step, keplerian_elements):
        """
        Initialisation function of GMAT interface.

        Parameters
        ----------
        start_time : astropy.time.core.Time
            Mission start time.
        end_time : astropy.time.core.Time
            Mission end time.
        time_step : astropy.time.core.TimeDelta
            Time step for output state.
        keplerian_elements : dict
            Earth-centered Keplerian elements of the satellite.

        Returns
        -------
        None.

        """

        # Define state variables
        self.start_time = start_time
        self.end_time = end_time
        self.time_step = time_step
        self.keplerian_elements = keplerian_elements

        # Declare empty variables
        self.spacecraft_frame = None

    def generate_script(self):
        """
        Function to generate script for GMAT.

        Returns
        -------
        None.

        """

        # Define substrings to identify lines
        spacecraft_keyword = "GMAT Spacecraft."
        output_keyword = "GMAT SpacecraftReport.Filename"
        mission_keyword = "Propagate 'SpacecraftPropagate' SpacecraftProp(Spacecraft)"

        # Calculate times in GMAT MJD format
        start_time = self.start_time.jd - GMAT_MJD_OFFSET
        end_time = self.end_time.jd - GMAT_MJD_OFFSET

        # Load script template
        with open(TEMPLATE_PATH, "r") as templatescript:
            script = templatescript.readlines()

        # Update script by iterating through the lines
        # TODO: write more elegant solution
        for iline, line in enumerate(script):
            # Update start and end time
            if spacecraft_keyword + "Epoch" in line:
                script[iline] = f"{spacecraft_keyword}Epoch = '{start_time}';\n"
            if mission_keyword in line:
                script[iline] = f"{mission_keyword} {{Spacecraft.UTCModJulian = {end_time}}};\n"

            # Update spacecraft elements
            if spacecraft_keyword in line:
                for element, value in self.keplerian_elements.items():
                    if spacecraft_keyword+element in line:
                        script[iline] = f"{spacecraft_keyword}{element} = {value};\n"

            # Update output path
            if output_keyword in line:
                script[iline] = f"{output_keyword} = '{OUTPUT_PATH}';\n"

        # Output modified script
        with open(MODIFIED_PATH, "w") as modified_script:
            modified_script.writelines(script)

    def execute_script(self):
        """
        Function to execute script with GMAT.

        Returns
        -------
        None.

        """

        # Define command to run GMAT
        command = "GMAT"
        # Define flags when running GMAT
        # (-r: run script, -m: run minimised, -x: exit when finished)
        flags = "-r -m -x"

        full_command = f"""{command} {flags} "{MODIFIED_PATH}"  """

        # Display progress bar in terminal
        with tqdm(total=1, desc="GMAT Exectution") as pbar:
            # Run GMAT
            os.system(full_command)
            # Update progress bar
            pbar.update(1)

    def load_state(self):
        """
        Function to load output from GMAT.

        Returns
        -------
        spacecraft_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
            Spacecraft reference frame relative to the Earth's centre of mass
            with the same orientation as BCRS/ICRS.

        """

        # Import GMAT output
        output = pd.read_fwf(OUTPUT_PATH)

        # Calculate time vector for interpolation
        nstep = np.rint((self.end_time-self.start_time)/self.time_step) + 1
        spacecraft_time = self.start_time + \
            self.time_step * np.arange(0, nstep)

        # Calculate GMAT time
        time = Time(output["Spacecraft.UTCModJulian"].values
                    + GMAT_MJD_OFFSET, format='jd')

        # Interpolate spacecraft state
        pos_x = np.interp(spacecraft_time.jd,
                          time.jd,
                          output["Spacecraft.EarthICRF.X"].values)
        pos_y = np.interp(spacecraft_time.jd,
                          time.jd,
                          output["Spacecraft.EarthICRF.Y"].values)
        pos_z = np.interp(spacecraft_time.jd,
                          time.jd,
                          output["Spacecraft.EarthICRF.Z"].values)
        vel_x = np.interp(spacecraft_time.jd,
                          time.jd,
                          output["Spacecraft.EarthICRF.VX"].values)
        vel_y = np.interp(spacecraft_time.jd,
                          time.jd,
                          output["Spacecraft.EarthICRF.VY"].values)
        vel_z = np.interp(spacecraft_time.jd,
                          time.jd,
                          output["Spacecraft.EarthICRF.VZ"].values)

        # Add astropy units to position and velocity
        spacecraft_position = CartesianRepresentation(x=pos_x,
                                                      y=pos_y,
                                                      z=pos_z,
                                                      unit=u.km)
        spacecraft_velocity = CartesianRepresentation(x=vel_x,
                                                      y=vel_y,
                                                      z=vel_z,
                                                      unit=u.km/u.s)

        # Generate spacecraft reference frame assuming that the EarthICRF
        # reference frame is equivalent to GCRS
        spacecraft_frame = GCRS(representation_type="cartesian",
                                obstime=spacecraft_time,
                                obsgeoloc=spacecraft_position,
                                obsgeovel=spacecraft_velocity)

        # Store spacecraft frame
        self.spacecraft_frame = spacecraft_frame

        return spacecraft_frame
