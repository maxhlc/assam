#!/usr/bin/env python

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from tqdm import tqdm
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
import multiprocessing


from cuda_methods import separation_cuda as separation_cuda


def unwrap_generate_bitmap(arg, **kwarg):
    """
    Wrapper function to enable multiprocessing of the generate_bitmap method,
    as found at:
        http://www.rueckstiess.net/research/snippets/show/ca1d7d90

    Parameters
    ----------
    arg
        Arguments.
    **kwarg
        Keyword arguments.

    Returns
    -------
    function
        Unwrapped generate bitmap function.

    """
    return VisualisationModule.generate_bitmap(*arg, **kwarg)


class VisualisationModule():

    def __init__(self, spacecraft_frame, solar_bodies, targets, npix=(721, 361), cuda=False):
        """
        Initialisation function for the visualisation module.

        Parameters
        ----------
        spacecraft_frame : astropy.coordinates.builtin_frames.gcrs.GCRS
            Spacecraft reference frame relative to the Earth's centre of mass
            with the same orientation as BCRS/ICRS.
        solar_bodies : list
            Solar system bodies and their properties.
        targets : list
            Targets and their properties.
        npix : tuple, optional
            Number of sample points in RA and DEC. The default is (721, 361).
        cuda : boolean, optional
            Flag to use CUDA. The default is False.

        Returns
        -------
        None.

        """

        # Import satellite frame, solar bodies, and targets
        self.spacecraft_frame = spacecraft_frame
        self.solar_bodies = solar_bodies
        self.targets = targets

        # Import CUDA functions
        self.cuda = cuda

        # Create angle vectors and mesh
        self.theta = np.linspace(-180, 180, npix[0]) * u.deg
        self.phi = np.linspace(-90, 90, npix[1]) * u.deg
        self.theta_grid, self.phi_grid = np.meshgrid(self.theta, self.phi)

    def generate_bitmap(self, index=0):
        """
        Function to generate visual bitmap.

        Parameters
        ----------
        index : int, optional
            Index for the generated timestep. The default is 0.

        Returns
        -------
        solar_bitmap : numpy.ndarray
            Boolean array of solar body visibility.
        target_bitmap : numpy.ndarray
            Boolean array of target visibility.

        """

        # Generate coordinate grid at index time
        frame = self.spacecraft_frame[index]
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
            if self.cuda:
                separation = separation_cuda(solar_body_coordinates,
                                             coordinates_grid)
            else:
                separation = solar_body_coordinates.separation(
                    coordinates_grid)

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
                if self.cuda:
                    separation = separation_cuda(subtarget_coordinates,
                                                 coordinates_grid)
                else:
                    separation = subtarget_coordinates.separation(
                        coordinates_grid)

                # Reshape to separation array
                separation_array = separation.reshape(self.theta_grid.shape)

                # Calculate subtarget array
                subtarget_array = separation_array <= subtarget.angular_radius

                # Update overall target bitmap array
                target_bitmap = np.logical_or(target_bitmap, subtarget_array)

        # Return bitmaps
        return solar_bitmap, target_bitmap

    def generate_bitmaps(self, num_workers=None):
        """
        Function to generate multiple bitmaps in one call.

        Parameters
        ----------
        num_workers : int, optional
            Number of workers for the multiprocessing pool. The default is None.

        Returns
        -------
        None.

        """

        # Declare bitmap lists
        # TODO: consider numpy arrays
        solar_bitmaps = []
        target_bitmaps = []

        # Find number of timesteps
        nindex = len(self.spacecraft_frame.obstime)

        # Generate bitmaps
        with multiprocessing.Pool(num_workers) as p:
            # Create progress bar
            with tqdm(total=nindex, desc="Bitmap Generation") as pbar:
                # Iterate through timesteps
                # TODO: find a more acceptable way to make this loop parallel
                for solar_bitmap, target_bitmap in p.imap(unwrap_generate_bitmap, zip([self]*nindex, range(nindex))):
                    # Store bitmaps
                    solar_bitmaps.append(solar_bitmap)
                    target_bitmaps.append(target_bitmap)
                    # Update progress bar
                    pbar.update()

        # Store bitmaps
        self.solar_bitmaps = solar_bitmaps
        self.target_bitmaps = target_bitmaps

    def __plot_bitmap(self, index=0):
        """
        Function to generate bitmap plot.

        Parameters
        ----------
        index : int, optional
            Index for the plotted timestep. The default is 0.

        Returns
        -------
        None.

        """

        # Extract observation time and bitmaps
        obstime = self.spacecraft_frame.obstime[index]
        solar_bitmap = self.solar_bitmaps[index]
        target_bitmap = self.target_bitmaps[index]

        # Create figure
        plt.figure(figsize=((5.5, 4)),
                   dpi=300)

        # Define colourmaps
        cmap_target = ListedColormap(["white", "green"])
        cmap_solar = ListedColormap(["white", "red"])

        # Plot target bitmap
        plt.contourf(self.theta_grid, self.phi_grid, target_bitmap,
                     cmap=cmap_target,
                     antialiased=False)

        # Plot solar bitmap
        plt.contourf(self.theta_grid, self.phi_grid, solar_bitmap,
                     cmap=cmap_solar,
                     alpha=0.5,
                     antialiased=False)

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
        """
        Function to plot multiple bitmaps in one call.

        Returns
        -------
        None.

        """

        # TODO: date range input

        # Find number of timesteps
        nindex = len(self.spacecraft_frame.obstime)

        # Iterate through timesteps
        # TODO: make parallel
        for index in tqdm(range(nindex), desc="Bitmap Plotting"):
            # Plot bitmaps
            self.__plot_bitmap(index)
