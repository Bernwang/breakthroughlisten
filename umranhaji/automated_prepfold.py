#This script takes all the .fil files in the directory and uses the docker imag\
e caseyjlaw/pulsar-psr to run the prepfold command on them.                     

import subprocess
subprocess.call('eval $(docker-machine env default)', shell=True)
subprocess.call('docker run caseyjlaw/pulsar-stack')
