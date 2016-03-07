#!/usr/bin/env python 

# This is an example how to make a plot in the Aitoff projection using data
# in a SkyCoord object. Here a randomly generated data set will be used. The
# final script can be found below.

# First we need to import the required packages. We use
# `matplotlib <http://www.matplotlib.org/>`_ here for
# plotting and `numpy <http://www.numpy.org/>`_  to get the value of pi and to
# generate our random data.

import sys
sys.path.append('/home/webdev/.local/lib/python2.6/site-packages')
import time
import matplotlib.pyplot as plt
import numpy as np
import redis
import os
from datetime import datetime
from pytz import timezone
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    from astropy import units as u
    from astropy.coordinates import SkyCoord

	
# So we know the last time the script has run
time = timezone('America/Los_Angeles')

# We now generate random data for visualisation. For RA this is done in the range
# of 0 and 360 degrees (``ra_random``), for DEC between -90 and +90 degrees
# (``dec_random``). Finally, we multiply these values by degrees to get an
# `~astropy.units.Quantity` with units of degrees.

r = redis.Redis(host='localhost', port=6380, db=0) # GBT

ra = float(r.hget('RA_DRV', 'VALUE')) * u.degree
dec = float(r.hget('DEC_DRV', 'VALUE')) * u.degree

# As next step, those coordinates are transformed into an astropy.coordinates
# astropy.coordinates.SkyCoord object.
c = SkyCoord(ra=ra, dec=dec, frame='icrs')

# Because matplotlib needs the coordinates in radians and between :math:`-\pi`
# and :math:`\pi`, not 0 and :math:`2\pi`, we have to convert them.
# For this purpose the `astropy.coordinates.Angle` object provides a special method,
# which we use here to wrap at 180:
ra_rad = c.ra.wrap_at(180 * u.deg).radian
dec_rad = c.dec.radian

# As last step we set up the plotting environment with matplotlib using the
# Aitoff projection with a specific title, a grid, filled circles as markers with
# a markersize of 2 and an alpha value of 0.3.

plt.figure(figsize=(8,4.2))
plt.subplot(111, projection="aitoff")
plt.title('Last img generated %s ' % datetime.now(time),  y=1.08)
plt.grid(True)
plt.plot(ra_rad, dec_rad, 'o', markersize=6, alpha=0.3)
plt.subplots_adjust(top=0.95,bottom=0.0)
plt.savefig("/home/webdev/html/status/images/gbtPreAitoff.png", dpi = 100)
plt.clf()

# Circumvent issue of website calling image during generation
os.rename("/home/webdev/html/status/images/gbtPreAitoff.png","/home/webdev/html/status/images/gbtAitoff.png")

