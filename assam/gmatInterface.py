#!/usr/bin/env python

import os
import pandas as pd
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import GCRS, CartesianRepresentation
from tqdm import tqdm

class gmatInterface():

    def __init__(self, start_time, end_time, keplerian_elements):
        """
        Initialisation function of GMAT interface.

        Parameters
        ----------
        start_time : astropy.time.core.Time
            Mission start time.
        end_time : astropy.time.core.Time
            Mission end time.
        keplerian_elements : dict
            Earth-centered Keplerian elements of the satellite.

        Returns
        -------
        None.

        """

        # Define state variables
        self.start_time = start_time
        self.end_time = end_time
        self.keplerian_elements = keplerian_elements

        # Retrieve current directory path
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # Define paths for GMAT files as GMAT requires absolute paths
        self.template_path = f"{dir_path}\\GMAT\\GMAT_template.script"
        self.modified_path = f"{dir_path}\\GMAT\\GMAT_modified.script"
        self.output_path = f"{dir_path}\\GMAT\\GMAT_output.dat"

        # Define offset for Modified Julian Dates
        # GMAT uses a non-standard offset, relative to 05 Jan 1941 12:00:00.000
        self.GMAT_MJD_OFFSET = 2430000.0

        return None

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
        start_time_GMAT = self.start_time.jd - self.GMAT_MJD_OFFSET
        end_time_GMAT = self.end_time.jd - self.GMAT_MJD_OFFSET

        # Load script template
        with open(self.template_path, "r") as templatescript:
            script = templatescript.readlines()

        # Update script by iterating through the lines
        # TODO: write more elegant solution
        for iline, line in enumerate(script):
            # Update start and end time
            if spacecraft_keyword + "Epoch" in line:
                script[iline] = f"{spacecraft_keyword}Epoch = '{start_time_GMAT}';\n"
            if mission_keyword in line:
                script[iline] = f"{mission_keyword} {{Spacecraft.UTCModJulian = {end_time_GMAT}}};\n"

            # Update spacecraft elements
            if spacecraft_keyword in line:
                for element, value in self.keplerian_elements.items():
                    if spacecraft_keyword+element in line:
                        script[iline] = f"{spacecraft_keyword}{element} = {value};\n"

            # Update output path
            if output_keyword in line:
                script[iline] = f"{output_keyword} = '{self.output_path}';\n"

        # Output modified script
        with open(self.modified_path, "w") as modifiedscript:
            modifiedscript.writelines(script)

        return None

    def execute_script(self):
        """
        Function to execute script with GMAT.

        Returns
        -------
        None.

        """
        
        # Define command to run GMAT
        GMAT_command = "GMAT"
        # Define flags when running GMAT
        # (-r: run script, -m: run minimised, -x: exit when finished)
        GMAT_flags = "-r -m -x"
        
        # Display progress bar in terminal
        with tqdm(total=1, desc="GMAT Exectution") as pbar:
            # Run GMAT
            os.system(f"""{GMAT_command} {GMAT_flags} "{self.modified_path}"  """)
            # Update progress bar
            pbar.update(1)
        
        return None

    def load_state(self):
        """
        Function to load output from GMAT.

        Returns
        -------
        satellite_state : astropy.coordinates.builtin_frames.gcrs.GCRS
            Satellite state in the GCRS reference frame.
        satellite_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
            Satellite reference frame relative to the Earth's centre of mass
            with the same orientation as BCRS/ICRS.

        """

        # Import GMAT output
        output_GMAT = pd.read_fwf(self.output_path)

        # Extract Modified Julian Dates, convert to Julian Dates,
        # and convert to astropy time
        satellite_time = Time(output_GMAT["Spacecraft.UTCModJulian"].values
                              + self.GMAT_MJD_OFFSET, format='jd')

        # Add astropy units to position and velocity
        satellite_position = CartesianRepresentation(
            x=output_GMAT["Spacecraft.EarthICRF.X"].values,
            y=output_GMAT["Spacecraft.EarthICRF.Y"].values,
            z=output_GMAT["Spacecraft.EarthICRF.Z"].values,
            unit=u.km)
        satellite_velocity = CartesianRepresentation(
            x=output_GMAT["Spacecraft.EarthICRF.VX"].values,
            y=output_GMAT["Spacecraft.EarthICRF.VY"].values,
            z=output_GMAT["Spacecraft.EarthICRF.VZ"].values,
            unit=u.km/u.s)

        # Generate satellite state assuming that the EarthICRF reference frame
        # is equivalent to GCRS
        # TODO: address error between astropy and GMAT frames
        satellite_state = GCRS(
            representation_type="cartesian",
            obstime=satellite_time,
            x=satellite_position.x,
            y=satellite_position.y,
            z=satellite_position.z)

        # Generate satellite reference frame assuming that the EarthICRF
        # reference frame is equivalent to GCRS
        satellite_frame = GCRS(
            representation_type="cartesian",
            obstime=satellite_time,
            obsgeoloc=satellite_position,
            obsgeovel=satellite_velocity)

        # Store outputs
        self.satellite_state = satellite_state
        self.satellite_frame = satellite_frame

        return satellite_state, satellite_frame
