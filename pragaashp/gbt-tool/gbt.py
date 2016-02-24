"""
A Bridge between GBTFilter and GBTScraper.

Note: For security reasons, querying the database will prompt the user for a password.

"""
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

from gbt_filter import *
from gbt_scraper import *
from getpass import getpass
from astroplan import AirmassConstraint,\
					  SunSeparationConstraint,\
					  AltitudeConstraint

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

	def getTargets(self,event_index):
		assert event_index < len(self.schedule), "Event Index out of range."
		e = self.schedule[event_index]
		gbfilter = GBTFilter(getpass(),e.start,e.end,self.constraints)
		result_table = gbfilter.applyFilter()
		result_table.meta['start date-time'] = e.start
		result_table.meta['end date-time'] = e.end
		return result_table

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

"""
Sample Usage: 

Set Constraints -> Initialize Class -> Get Schedule Info -> Get Observable Targets

"""
if __name__ == "__main__":
	# - - - - - - MODIFY CONSTRAINTS HERE - - - - - - - - #
	constraints = [AltitudeConstraint(40*u.deg,80*u.deg)]
	# - - - - - - - - - - - - - - - - - - - - - - - - - - #
	gbto = GBTObservables(constraints)
	gbto.getTargets(0).show_in_browser(jsviewer=True)
