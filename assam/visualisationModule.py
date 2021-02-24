#!/usr/bin/env python

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from tqdm import tqdm
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap


class visualisationModule():

    def __init__(self, satellite_frame, solar_bodies, targets, npix=(1441, 721)):
        # TODO: docstring

        # Import satellite frame, solar bodies, and targets
        self.satellite_frame = satellite_frame
        self.solar_bodies = solar_bodies
        self.targets = targets

        # Create angle vectors and mesh
        self.theta = np.linspace(-180, 180, npix[0]) * u.deg
        self.phi = np.linspace(-90, 90, npix[1]) * u.deg
        self.theta_grid, self.phi_grid = np.meshgrid(self.theta, self.phi)

    def __generate_bitmap(self, index=0):
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

        # Return bitmaps
        return solar_bitmap, target_bitmap

    def generate_bitmaps(self):
        # TODO: docstring

        # Declare bitmap lists
        # TODO: consider numpy arrays
        solar_bitmaps = []
        target_bitmaps = []

        # Find number of timesteps
        nindex = len(self.satellite_frame.obstime)

        # Iterate through timesteps
        # TODO: make parallel
        for index in tqdm(range(nindex), desc="Bitmap Generation"):
            # Calculate bitmaps
            solar_bitmap, target_bitmap = self.__generate_bitmap(index)

            # Store bitmaps
            solar_bitmaps.append(solar_bitmap)
            target_bitmaps.append(target_bitmap)

        # Store bitmaps
        self.solar_bitmaps = solar_bitmaps
        self.target_bitmaps = target_bitmaps

    def __plot_bitmap(self, obstime, solar_bitmap, target_bitmap):
        # TODO: docstring

        # Create figure
        plt.figure(figsize=((5.5, 4)),
                   dpi=300)

        # Define colourmaps
        cmap_target = ListedColormap(["white", "green"])
        cmap_solar = ListedColormap(["white", "red"])

        # Plot target bitmap
        plt.contourf(self.theta_grid, self.phi_grid, target_bitmap,
                     cmap=cmap_target)

        # Plot solar bitmap
        plt.contourf(self.theta_grid, self.phi_grid, solar_bitmap,
                     cmap=cmap_solar,
                     alpha=0.5)

        # Reverse axes
        ax = plt.gca()
        ax.invert_xaxis()

        # Set square aspect
        ax.set_aspect(aspect=1)

        # Add axis labels
        plt.xlabel("RA [deg]")
        plt.ylabel("DEC [deg]")

        # Set ticks
        plt.xticks(np.arange(-180, 240, step=60))
        plt.yticks(np.arange(-90, 120, step=30))

        # Add grid
        plt.grid(alpha=0.25)

        # Add datetime in text box
        textstr = obstime.fits
        props = dict(boxstyle="round", facecolor="white", alpha=0.75)
        ax.text(0.975, 0.95,
                textstr,
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment="top",
                horizontalalignment="right",
                bbox=props)

    def plot_bitmaps(self):
        # TODO: docstring

        # TODO: date range input

        # Find number of timesteps
        nindex = len(self.satellite_frame.obstime)

        # Iterate through timesteps
        # TODO: make parallel
        for index in tqdm(range(nindex), desc="Bitmap Plotting"):
            # Extract observation time and bitmaps
            obstime = self.satellite_frame.obstime[index]
            solar_bitmap = self.solar_bitmaps[index]
            target_bitmap = self.target_bitmaps[index]

            # Plot bitmaps
            self.__plot_bitmap(obstime, solar_bitmap, target_bitmap)
