#!/usr/bin/env python

import os
import pandas as pd
from astropy.time import Time
from astropy import units as u
from astropy.table import QTable

def run_gmat(start_time,end_time,keplerian_elements):
    """
    Function to run GMAT.

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
    satellite_state : astropy.table.table.QTable
        Table with satellite state in Cartesian form in the
        MJ2000Eq reference frame.

    """
    
    def generate_script():
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
        start_time_GMAT = start_time.jd - GMAT_MJD_OFFSET
        end_time_GMAT = end_time.jd - GMAT_MJD_OFFSET
        
        # Load script template
        with open(template_path,"r") as templatescript:
            script = templatescript.readlines()
            
        # Update script by iterating through the lines
        for iline, line in enumerate(script):
            # Update start and end time
            if spacecraft_keyword + "Epoch" in line:
                script[iline] = f"{spacecraft_keyword}Epoch = '{start_time_GMAT}';\n"
            if mission_keyword in line:
                script[iline] = f"{mission_keyword} {{Spacecraft.UTCModJulian = {end_time_GMAT}}};\n"
            
            # Update spacecraft elements
            if spacecraft_keyword in line:
                for element, value in keplerian_elements.items():
                    if spacecraft_keyword+element in line:
                        script[iline] = f"{spacecraft_keyword}{element} = {value};\n"
                        
            # Update output path
            if output_keyword in line:
                script[iline] = f"{output_keyword} = '{output_path}';\n"
                
        # Output modified script
        with open(modified_path,"w") as modifiedscript:
            modifiedscript.writelines(script)

        return None
    
    
    def execute_script():
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
        
        # Run GMAT
        os.system(f"""{GMAT_command} {GMAT_flags} "{modified_path}"  """)
        
        return None  
    
    
    def load_output():
        """
        Function to load output from GMAT.

        Returns
        -------
        output : astropy.table.table.QTable
            Table with satellite state in Cartesian form in the
            MJ2000Eq reference frame.

        """
        
        # Import GMAT output
        output_GMAT = pd.read_fwf(output_path)
        
        # Extract Modified Julian Dates, convert to Julian Dates,
        # and convert to astropy time
        jd = Time(output_GMAT["Spacecraft.UTCModJulian"].values 
                  + GMAT_MJD_OFFSET,format='jd')
        
        # Add astropy units to position and velocity
        x = output_GMAT["Spacecraft.EarthMJ2000Eq.X"].values * u.km
        y = output_GMAT["Spacecraft.EarthMJ2000Eq.Y"].values * u.km
        z = output_GMAT["Spacecraft.EarthMJ2000Eq.Z"].values * u.km
        vx = output_GMAT["Spacecraft.EarthMJ2000Eq.VX"].values * u.km / u.s
        vy = output_GMAT["Spacecraft.EarthMJ2000Eq.VY"].values * u.km / u.s
        vz = output_GMAT["Spacecraft.EarthMJ2000Eq.VZ"].values * u.km / u.s
        
        # Combine into astropy QTable       
        satellite_state = QTable([jd, x, y, z, vx, vy, vz],
                        names=("JD","X","Y","Z","VX","VY","VZ"))
        
        return satellite_state
    
    
    # Define offset for Modified Julian Dates
    # GMAT uses a non-standard offset, relative to 05 Jan 1941 12:00:00.000
    GMAT_MJD_OFFSET = 2430000.0
    
    # Retrieve current directory path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Define paths for GMAT files
    template_path = f"{dir_path}\GMAT\\GMAT_template.script"
    modified_path = f"{dir_path}\GMAT\\GMAT_modified.script"
    output_path = f"{dir_path}\GMAT\\GMAT_output.dat"
    
    # Generate script, execute, and load output
    generate_script()
    execute_script()
    satellite_state = load_output()
    
    return satellite_state