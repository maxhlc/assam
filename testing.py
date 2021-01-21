# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 13:42:12 2021

@author: Max
"""

import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body, GCRS

mjd = np.linspace(59000,60000,201)

t = Time(mjd,format='mjd')

t = Time(t,format='iso')

with solar_system_ephemeris.set('builtin'):
    ear = get_body('earth', t)
    jup = get_body('jupiter', t)
    
satellite_frame = GCRS(obstime=t,obsgeoloc=[1, 2, 3]*u.m)

ear=ear.transform_to(satellite_frame)

fig, ax = plt.subplots()
ax.plot(mjd,ear.ra)

fig, ax = plt.subplots()
ax.plot(mjd,ear.dec)

fig, ax = plt.subplots()
ax.plot(mjd,ear.distance)