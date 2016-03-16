#!/usr/bin/env python

"""
Interfaces with Redis database
"""

import cgi
import cgitb
cgitb.enable()
import sys
sys.path.append('/home/webdev/.local/lib/python2.6/site-packages')
import redis
import HTML


# Constants and Parameters
r = redis.Redis(host='localhost', port=6380, db=0)
projName = 'AGBT16A_999' # BTL Project name on Cleo


def htmlStart():
    """
    Includes beginning content required for html
    """

    print "Content-Type: text/html"
    print # this print is necessary, it denotes end of header

    print '''
    <html>
    <body>
    '''

    return True

def htmlEnd():
    """
    Includes ending content required for html
    """

    print '''
    </body>
    </html>
    '''

    return True

def statusImg(status):
	'''
	Prints image tag for on-switch if Redis key is on, off-switch if off
	'''

	if status == True:
		img = '<i id="gbt-statusImg" class="fa fa-thumbs-o-up fa-5x"></i>'
	else:
		img = '<i id="gbt-statusImg" class="fa fa-thumbs-o-down fa-5x"></i>'

	return img

def statusTxt(status):
	'''
	Prints GBT status text
	'''

	if status == True:
		text = 'Currently observing for Breakthough Listen'
	else:
		text = 'Not currently observing Breakthrough Listen targets'

	text =  """
            <p id="gbt-statusTxt">
            Green Bank Telescope<br>
            %s <br>

            <a href="./gbt-short.html">More Details</a>
           
	    </p>
            """ %text

	return text

def main():
    currentProj = r.hget('SCPROJID','VALUE')

    htmlStart()
    if projName in currentProj:
        print statusImg(True)
        print statusTxt(True)
    else:
        print statusImg(False)
        print statusTxt(False)
    htmlEnd()


if __name__ == "__main__":
    main()























