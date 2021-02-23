#!/usr/bin/env python

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from matplotlib import pyplot as plt


class visualModule():

    def __init__(self, satellite_frame, solar_bodies, targets, ntheta=1441, nphi=721):
        # TODO: docstring

        # Import satellite frame, solar bodies, and targets
        self.satellite_frame = satellite_frame
        self.solar_bodies = solar_bodies
        self.targets = targets

        # Create angle vectors and mesh
        self.theta = np.linspace(-180, 180, ntheta) * u.deg
        self.phi = np.linspace(-90, 90, nphi) * u.deg
        self.theta_grid, self.phi_grid = np.meshgrid(self.theta, self.phi)

    def generate_bitmap(self, index=0):
        # TODO: docstring
        
        # TODO: change behaviour: calculate all bitmaps together then plot separately

        # Generate coordinate grid at index time
        frame = self.satellite_frame[index]
        frame.representation_type = "spherical"
        coordinates_grid = SkyCoord(ra=self.theta_grid.ravel(),
                                    dec=self.phi_grid.ravel(),
                                    frame=frame)

        # Generate bitmap array (all pixels false initially)
        solar_bitmap = np.empty(self.theta_grid.shape)
        solar_bitmap.fill(False)
        
        target_bitmap = np.empty(self.theta_grid.shape)
        target_bitmap.fill(False)

        # Iterate through planets
        for solar_body in self.solar_bodies:
            # Extract solar body coordinates
            solar_body_coordinates = solar_body.coordinates[index]

            # Calculate separation vector
            separation = solar_body_coordinates.separation(coordinates_grid)

            # Reshape to separation array
            separation_array = separation.reshape(self.theta_grid.shape)

            # Calculate hard radius array
            hard_radius_array = separation_array <= solar_body.angular_radius[index]

            # Calculate soft radius array
            soft_radius_array = np.empty(self.theta_grid.shape)
            soft_radius_array.fill(False)
            for (r1, r2) in solar_body.soft_radius:
                soft_radius_temp = np.logical_and(
                    separation_array >= r1, separation_array <= r2)
                soft_radius_array = np.logical_or(
                    soft_radius_array, soft_radius_temp)

            # Calculate solar body bitmap
            # TODO: store bitmaps for each solar body
            solar_body_bitmap = np.logical_or(
                hard_radius_array, soft_radius_array)

            # Update overall solar body bitmap array
            # TODO: update method to combine bitmaps
            solar_bitmap = np.logical_or(solar_bitmap, solar_body_bitmap)

        # Iterate through targets
        # TODO: store bitmaps per target
        for target in self.targets:
            for subtarget in target.subtargets:
                # Extract target coordinates
                subtarget_coordinates = subtarget.coordinates[index]
                
                # Calculate separation vector
                separation = subtarget_coordinates.separation(coordinates_grid)
                
                # Reshape to separation array
                separation_array = separation.reshape(self.theta_grid.shape)
                
                # Calculate subtarget array
                subtarget_array = separation_array <= subtarget.angular_radius
                
                # Update overall target bitmap array
                target_bitmap = np.logical_or(target_bitmap, subtarget_array)
        
        # Store bitmaps
        self.solar_bitmap = solar_bitmap
        self.target_bitmap = target_bitmap

    def plot_bitmap(self, index=0):
        # TODO: docstring

        # Create figure
        plt.figure(figsize=((5.5, 4)),
                   dpi=300)
        
        # Define colourmaps
        cmap_target = None
        cmap_solar = None
        
        # Plot target bitmap
        plt.contourf(self.theta_grid, self.phi_grid, self.target_bitmap,
                     cmap="Greens")       

        # Plot solar bitmap
        plt.contourf(self.theta_grid, self.phi_grid, self.solar_bitmap,
                     cmap="Reds",
                     alpha=0.5)

        # Reverse axes
        ax = plt.gca()
        ax.invert_xaxis()
        
        # Set square aspect
        ax.set_aspect(aspect=1)

        # Add axis labels
        plt.xlabel("RA [deg]")
        plt.ylabel("DEC [deg]")

        # Add grid
        plt.grid()
        
        # Add datetime in text box
        textstr = self.satellite_frame.obstime[index].fits
        props = dict(boxstyle="round", facecolor="white", alpha=0.75)
        ax.text(0.975, 0.95,
                textstr,
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment="top",
                horizontalalignment="right",
                bbox=props)