Casey Law set up some analysis tools in a Docker image, which is a bit like a virtual machine. This enables an easy install of the standard tools used to analyze pulsar data. We observe one pulsar at the beginning of each Breakthrough Listen observing run to make sure that the system is working properly. Ultimately we want to implement quality control and diagnostics on our data based on what the output plots look like.

Steps to get the software running:

1. Ensure you have a working Python installation. https://www.continuum.io/downloads is a good one.

2. Install Docker from https://www.docker.com/products/docker-toolbox

3. In a terminal, install Casey Law's Python tools to access tools on the Docker image:
pip install -e git+https://github.com/caseyjlaw/sidomo.git#egg=sidomo

4. Install the pulsar tools Docker image:
docker pull caseyjlaw/pulsar-stack

5. Grab one of the Breakthrough Listen pulsar data files. You can pick one from
http://setiathome.berkeley.edu/~mattl/files.html

For example, blc4_guppi_57407_61054_PSR_J1840+5640_0004.fil - the filename format here is:
blc4 - Breakthrough Listen Compute node 4 (there are 8 compute nodes numbered from 0 - 7)
guppi - the GBT pulsar instrument
57407 - Modified Julian Date of the observation
61054 - number of seconds since start of the day
PSR_J1840+5640 - name of the pulsar:
	PSR - identifies it as a pulsar
	J - Julian epoch
	1840 - Right Ascension 18 hours 40 minutes
	5640 - Declination 56 degrees 40 minutes
0004 - 
.fil - this is a filterbank file. For an explanation of the different kinds of files, read https://github.com/stevecroft/breakthrough-listen/blob/master/GBT/waterfall.txt

6. Now run prepfold on the pulsar data. Pulsars emit regular pulses, but these are often too faint to be detected individually, so astronomers need to "fold" the data on the pulsar period. Then various statistics of the pulsar can be determined. This is also a good test of the integrity of the telescope, data, and our systems.

cd to the directory containing the file you just downloaded, and then run

dodo -- prepfold blc4_guppi_57407_61054_PSR_J1840+5640_0004.fil -psr J1840+5640 -nosearch

(change the -psr option to match the name of the pulsar that we are looking at)

It should then spit out a bunch of information about the pulsar, and write several files including a Postscript plot. You can view this directly or convert to PDF. On a Mac you could run something like

ps2pdf blc4_guppi_57407_61054_PSR_J1840+5640_0004_PSR_J1840+5640.pfd.ps
open blc4_guppi_57407_61054_PSR_J1840+5640_0004_PSR_J1840+5640.pfd.pdf

You can see this example file right here in the repository.

