#!/usr/bin/env python

"""
Gets select keywords from Redis database
"""

import sys
sys.path.append('/home/webdev/.local/lib/python2.6/site-packages')
import cgi
import cgitb; cgitb.enable()
import redis
import HTML


# Constants and Parameters
r = redis.Redis(host='localhost', port=6380, db=0)
projName = 'AGBT16A_999' # BTL Project name on Cleo


def htmlStart():
	print "Content-Type: text/html"
	print # this print is necessary, it denotes end of header

	print '''
	<html>
	<body>
	'''

	return True

def htmlEnd():
	print '''
	</body>
	</html>
	'''

	return True

def getKeys(status):
	'''
	Prints image tag for on-switch if Redis key is on, off-switch if off
	'''

	keys = {
			'LASTUPDT': r.hget('LASTUPDT', 'VALUE'),
			'RA': r.hget('RA_DRV', 'VALUE'),
			'DEC': r.hget('DEC_DRV', 'VALUE'),
			'FREQ': r.hget('FREQ', 'VALUE')
			}

	if status == True:
		keys['STATUS'] = 'Breakthrough Listen is currently observing'
	else:
		keys['STATUS'] = 'Breakthrough Listen is currently not observing'

	p = '''
		<p id="gbt-target">
		%s <br>
		Last Green Bank Telescope update (EST): %s <br>
		Target Frequency: %s <br>
		Target Right Ascension: %s <br>
		Target Declination: %s <br>
		<p>
		''' %(
		      keys['STATUS'], 
		      keys['LASTUPDT'], 
		      keys['FREQ'],
		      keys['RA'], 
		      keys['DEC']
		      )

	return p

def main():
    currentProj = r.hget('SCPROJID','VALUE')

    htmlStart()
    if projName in currentProj:
    	print getKeys(True)
    else:
    	print getKeys(False)
    htmlEnd()


if __name__ == "__main__":
    main()


