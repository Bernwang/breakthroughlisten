'''
Gets ADC images from Redis
'''

# import os
import redis
import fnmatch
import subprocess as sp

r = redis.Redis(host='localhost', port=6380, db=0)

ADCSNAPS = fnmatch.filter(r.keys(), 'ADC?SNAP')

for ADC in ADCSNAPS:
    # os.system("redis-cli -p 6380 --raw get '%s' >  /home/webdev/html/status/images/%s.png" % (ADC, ADC))
    p = sp.Popen("redis-cli -p 6380 --raw get '%s' >  /home/webdev/html/status/images/%s.png" % (ADC, ADC), shell=True)
