"""
A Bridge between GBTFilter and GBTScraper.

Note: For security reasons, querying the database will prompt the user for a password.

"""
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

from gbt_filter import *
from gbt_scraper import *
from getpass import getpass
import os, shutil, json, webbrowser
from glob import glob

from astroplan.plots import plot_sky
from astroplan.utils import time_grid_from_range as genTimeSequence
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from astropy.table import Table
from matplotlib import cm

from astroplan import AirmassConstraint,\
					  SunSeparationConstraint,\
					  AltitudeConstraint,\
					  MoonSeparationConstraint

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

I_DIR = './html/img/'
G_DIR = './html/img/globals/'
T_DIR = './html/img/targets/'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

class GBTObservables():

	def __init__(self,constraints,date=None,days=5):
		self.schedule = self.__getSchedule__(date=date,days=days)
		self.constraints = constraints

	def __getSchedule__(self,date=None,days=5):
		scraper = GBTScraper(date,days)
		scraper.make()
		return scraper.btlpSchedule

	def viewSchedule(self,event_index):
		assert event_index < len(self.schedule), "Event Index out of range."
		print self.schedule[event_index]

	def viewScheduleAsTable(self):
		schedule = Table(rows=[(i,s.start+' PST',s.end+' PST') for i,s in enumerate(self.schedule)],\
					 names=('INDEX','START','END'),dtype=('u8','S20','S20'))
		schedule['INDEX'].format = '^9d'
		schedule['START'].format = '^26s'
		schedule['END'].format = '^26s'
		print '\n'+str(schedule)

	def getTargets(self,event_index):
		assert event_index < len(self.schedule), "Event Index out of range."
		e = self.schedule[event_index]
		gbfilter = GBTFilter(getpass(),e.start,e.end,self.constraints)
		filtered_targets = gbfilter.applyFilter()
		return (gbfilter,filtered_targets)

	def generateGlobalPlots(self,gbt_filter_obj,filtered_targets):
		self.__makedir__(I_DIR)
		self.__removedir__(G_DIR)
		self.__makedir__(G_DIR)
		self.__multi_target_plot__(gbt_filter_obj.gbt,Time(gbt_filter_obj.time_range.value[0]),\
		                           filtered_targets,'start')
		self.__multi_target_plot__(gbt_filter_obj.gbt,Time(gbt_filter_obj.time_range.value[1]),\
		                           filtered_targets,'end')

	def generatePathPlots(self,gbt_filter_obj,filtered_targets):
		self.__makedir__(I_DIR)
		self.__removedir__(T_DIR)
		self.__makedir__(T_DIR)
		times = genTimeSequence(gbt_filter_obj.time_range)
		total = len(filtered_targets)
		for i,t in enumerate(filtered_targets):
			self.__single_target_path_plot__(gbt_filter_obj.gbt,times,t,i,total)

	def __multi_target_plot__(self,observer,time,targets,name):
		cmap = cm.Set1
		for i, t in enumerate(targets):
		    ax = plot_sky(t,observer,time,\
		    	          style_kwargs=dict(color=cmap(float(i)/len(T)),label=t.name))
		fontP = FontProperties()
		fontP.set_size('small')
		lgd = plt.legend(prop=fontP,loc='center left',bbox_to_anchor=(1.25, 0.5), ncol=2)
		art = [lgd]
		fig = plt.gcf()
		fig.savefig('{0}{1}.png'.format(G_DIR,name), additional_artists=art, dpi=100,\
		            bbox_inches='tight')
		fig.clear()

	def __single_target_path_plot__(self,observer,times,target,tidx,total):
		cmap = cm.Set1
		ax = plot_sky(target,observer,times,\
			          style_kwargs=dict(color=cmap(float(tidx)/total),label=target.name))
		fontP = FontProperties()
		fontP.set_size('small')
		lgd = plt.legend(prop=fontP,loc='center left',bbox_to_anchor=(1.25, 0.5), ncol=2)
		art = [lgd]
		fig = plt.gcf()
		fig.savefig('{0}{1}.png'.format(T_DIR,target.name), additional_artists=art, dpi=100,\
		            bbox_inches='tight')
		fig.clear()

	def __makedir__(self,dir):
		if len(glob(dir)) == 0: os.mkdir(dir)

	def __removedir__(self,dir):
		if len(glob(dir)) > 0: shutil.rmtree(dir)

	def build_json_data(self,start,end,targets):
		schedule = {'title':'Current Schedule',\
					'start':'Start: '+start+' PST',\
					'end':'End: '+end+' PST'}
		targets = sorted([{'name':t.name,'ra':round(t.ra.value,4),'dec':round(t.dec.value,4)} \
					for t in targets],key=lambda x: x['name'])
		data = {'schedule': schedule, 'targets': targets}
		with open('./html/data.json','w') as fp:
			json.dump(data,fp)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

"""
Sample Usage: 

Set Constraints -> Initialize Class -> Get Schedule Info -> Get Observable Targets

"""
if __name__ == "__main__":

	# - - - - - - - - - - - - - - - - MODIFY CONSTRAINTS HERE - - - - - - - - - - - - - - - - - #
	constraints = [AltitudeConstraint(20*u.deg,80*u.deg),SunSeparationConstraint(20*u.deg,None),\
			   	   MoonSeparationConstraint(20*u.deg,None)]
	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

	print '\nInitializing...\n'
	G = GBTObservables(constraints)
	G.viewScheduleAsTable()

	selected_index = input('\nSelect Schedule Index: ')

	print '\nSelected Schedule: \n' + '- '*40
	G.viewSchedule(selected_index)
	print '- '*40

	print '\nAcquiring Targets...\n'
	F,T = G.getTargets(selected_index)

	table = Table(rows=[(t.name,t.ra.value,t.dec.value) for t in T],\
				  names=('target name','right ascension','declination'),\
				  dtype=('S17','f8','f8'))

	print '\nGenerating Plots...'
	G.generateGlobalPlots(F,T)
	G.generatePathPlots(F,T)

	selschedule = G.schedule[selected_index]
	G.build_json_data(selschedule.start,selschedule.end,T)

	print '\nDashboard serving at http://localhost:8000.'
	webbrowser.open('http://localhost:8000')