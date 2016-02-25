"""
Plotting script for gbt observable targets.

"""
from gbt import *
from astroplan.plots import plot_sky
import matplotlib.pyplot as plt
# from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from astropy.table import Table
from matplotlib import cm

constraints = [AltitudeConstraint(20*u.deg,80*u.deg),SunSeparationConstraint(20*u.deg,None),\
			   MoonSeparationConstraint(20*u.deg,None)]
G = GBTObservables(constraints)
F,T = G.getTargets(1)

G.viewSchedule(1)

table = Table(rows=[(t.name,t.ra.value,t.dec.value) for t in T],\
			  names=('target name','right ascension','declination'),\
			  dtype=('S8','f8','f8'))

cmap = cm.Set1  
for i, t in enumerate(T):
    ax = plot_sky(t, F.gbt, F.time_range, style_kwargs=dict(color=cmap(float(i)/len(T)),label=t.name))

fontP = FontProperties()
fontP.set_size('small')

lgd = plt.legend(prop=fontP,loc='center left',bbox_to_anchor=(1.25, 0.5), ncol=2)
art = [lgd]

fig = plt.gcf()
fig.savefig('obs-plot.png', additional_artists=art, dpi=300, bbox_inches='tight')

table.show_in_browser(jsviewer=True)