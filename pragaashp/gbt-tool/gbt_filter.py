"""
Filter Targets in MySQL Database based on their RA and DEC using sqlalchemy, astropy, and
astroplan.

"""
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

from time import mktime, gmtime, strptime, strftime
from gbt_mp import *
import astropy.units as u
from astropy.time import Time
from astropy.table import Table
from pytz import timezone
from astroplan import Observer, FixedTarget, is_always_observable
from sqlalchemy import create_engine, orm
from sqlalchemy.ext.automap import automap_base

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

from astropy.utils import iers 
iers.IERS.iers_table = iers.IERS_A.open('./iers.all')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

NUM_PROCESSES = 8

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

class GBTFilter():

	def __init__(self,db_pass,start_time,end_time,constraints):
		self.engine = self.__launch__(pwd=db_pass)
		self.targets = self.__get_targets__()
		self.time_range = Time([self.__pst2utc__(start_time),self.__pst2utc__(end_time)])
		self.constraints = constraints
		self.gbt = Observer(name = 'Green Bank Telescope',\
					   longitude = -79.839722 * u.deg,\
		 			   latitude = 38.433056 * u.deg,\
		 			   elevation = 880 * u.m,\
					   timezone = timezone('US/Eastern'))

	def __launch__(self,pwd=None,host='127.0.0.1',user='root',db='BLtargets'):
		route = "mysql://{0}:{1}@{2}:3307/{3}".format(user,pwd,host,db)
		return create_engine(route,echo=False)

	def __get_targets__(self):
		Base = automap_base()
		Base.prepare(self.engine,reflect=True)
		T = Base.classes.get('five_50_pc_sample')
		session = orm.Session(self.engine)
		# - - - - - - - - - - - - - - - - UNIPROCESS EXECUTION - - - - - - - - - - - - - - - #
		# targets = [FixedTarget(coord=SkyCoord(ra=t_ra*u.deg,dec=t_dec*u.deg),name=t_id) \  #
		# 		   for t_id,t_ra,t_dec in session.query(T.gal_id, T.ra, T.decl).\			 #
		# 		   order_by(T.gal_id)]														 #
		# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#
		data = session.query(T.star_id, T.Name, T.RA, T.DECL).order_by(T.star_id).all()
		targets = mp_build(NUM_PROCESSES,FixedTarget,data)
		session.close()
		return targets

	def __pst2utc__(self,time):
		time_format = '%Y-%m-%d %H:%M'
		pst = mktime(strptime(time + ' PST',time_format + ' %Z'))
		return strftime(time_format,gmtime(pst))

	def applyFilter(self):
		# - - - - - - - - - - - - - - - - UNIPROCESS EXECUTION - - - - - - - - - - - - - - - #
		# target_filter = is_observable(self.constraints,self.gbt,\				 			 #
		# 							  self.targets,time_range=self.time_range)				 #
		# return Table(rows=[(t.name,t.ra.value,t.dec.value) for t in \				 		 #
		# 			 compress(self.targets,target_filter)],names=('target id',\				 #
		# 			 'right ascension','declination'),dtype=('u4','f8','f8'))				 #
		# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#
		target_filter = mp_filter(NUM_PROCESSES,is_always_observable,constraints=self.constraints,\
		                                                             observer=self.gbt,\
		                                                             data=self.targets,\
		                                                             time_range=self.time_range)
		assert len(target_filter) > 0, "No observable targets found for given times and constraints."
		return target_filter

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #