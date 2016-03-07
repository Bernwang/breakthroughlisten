#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# This prints metadata to iframe directly from redis server

import sys
sys.path.append('/home/webdev/.local/lib/python2.6/site-packages')
import cgi
import cgitb
import redis
import HTML

cgitb.enable()


print "Content-Type: text/html"
print # this print is necessary, it denotes end of header


print '''
<html>
<body>
'''

# GBT
print '<div id = "gbtMeta">'
r = redis.Redis(host='localhost', port=6380, db=0)


# GBT metadata
keys = r.keys('*')
keys.sort()
strKeys = []
strVals = []
for key in keys:
        if r.type(key) == "string":
                if len(r.get(key)) <30:
                        strKeys.append(key)
                        strVals.append(r.get(key))
	if r.type(key) == 'hash':
				for subkey in r.hgetall(key).keys():
					if len(r.hget(key,subkey)) < 30: # Arbitrary amount
						keySubkey = key + ' ' + subkey
						strKeys.append(keySubkey)
						strVals.append(r.hget(key,subkey))
metrics = zip(strKeys,strVals)
metrics.sort()
table = HTML.Table(metrics)
table.style = ""
table.border = ""
table.cellpadding = "0"
print '<h4>GBT Metadata</h4>'
print table
print '</div>'
# print "<br>" + "<br>"


# # Arecibo
# print '<div id = "areciboMeta">'
# r = redis.Redis(host='localhost', port=6381, db=0)

# # Arecibo metadata
# keys = r.keys('*')
# keys = [key for key in keys if 'SCRAM' in key] # There's many testing values to filter out
# keys.sort()
# strKeys = []
# strVals = []
# for key in keys:
#         if r.type(key) == "string":
# 		if len(r.get(key)) < 30:
#                  	strKeys.append(key)
#                  	strVals.append(r.get(key))
#         if r.type(key) == 'hash':
#                         for subkey in r.hgetall(key).keys():
# 				if len(r.hget(key,subkey)) < 30:
#                                 	keySubkey = key + ' ' + subkey
#                                 	strKeys.append(keySubkey)
#                                 	strVals.append(r.hget(key,subkey))
# metrics = zip(strKeys,strVals)
# metrics.sort()
# table = HTML.Table(metrics)
# table.style = ""
# table.border = ""
# table.cellpadding = "0"
# print table
# print '</div>'


print '''
</body>
</html>
'''
