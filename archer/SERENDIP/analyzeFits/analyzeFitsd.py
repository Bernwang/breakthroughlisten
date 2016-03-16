"""
Runs analyzeFits.py on newest, unanalyzed FITS file
"""

import os
import sys
import glob
import subprocess
import psutil
import argparse
import logging


# Parameters
pidFile = '/tmp/analyzeFits.pid'

# Arguments
parser = argparse.ArgumentParser(description= "Manages PID lockfile for analyzeFits.py")
parser.add_argument('analyzeFits', help="Path to analyzeFits.py")
parser.add_argument('fitsDir', help="Path to FITS file directory")
parser.add_argument('sumDir', help="Path to desired summary directory")
parser.add_argument('source', help="Source name, e.g. gbt, ao")
parser.add_argument('--level', help="Set logging level, see logging module for help",
                    default='WARNING')
parser.add_argument('--log', help="Path to log", default='log.txt')
args = parser.parse_args()

# Logging
logLevel = getattr(logging, args.level.upper())
logging.basicConfig(filename=args.log, level=logLevel)


# Check PID if project is running
def statusPID(pidFile, source):
	"""
	True if process is running, false otherwise
	"""

	if os.path.isfile(pidFile):
		with open(pidFile) as infile:
			content = [line for line in infile.read().splitlines() if line]

		# Check if relevant PID is running
		for line in content:
			if source in line:
				PID = line.split('_')[0]

				try:
					P = psutil.Process(int(PID))

					if any('analyzeFits' in string for string in P.cmdline()):
						return True
					else: # PID running isn't relevant
						return False 
				except psutil.NoSuchProcess:
					return False

	else: # No PID file exists/was found
		# Create new file
		open(pidFile, 'w').close()
		return False 

def writePID(newPID, source):
	# Save PID to file. One PID per line.
	with open(pidFile, 'r+') as infile:
		content = [line for line in infile.read().splitlines() if line]

		# Purge all old PIDs
		savePIDs = [line for line in content if source not in line]

		# Add new PID
		savePIDs.append(str(newPID)+'_'+source)

		with open(pidFile, 'w+') as outfile:
			outfile.write('\n'.join(savePIDs))

def getNewest(fitsDir, sumDir):
	"""
	Returns newest, unprocessed file
	"""

	# Get list of current fits files in fitsDir
	files = []
	for (dirpath, dirnames, filenames) in os.walk(fitsDir):
		files.extend([os.path.join(dirpath, f) for f in filenames if 'fits' in f])

	# Get list of summaries created by analyzeFits.py. Used to see if fits
	# file has been processed yet.
	summaries = []
	for (dirpath, dirnames, filenames) in os.walk(sumDir):
		summaries.extend([os.path.join(dirpath, f) for f in filenames if 'summary' in f])

	# Compare files and summaries. Make list of unprocessed files.
	unprocessed = []
	for f in files:
		flag = 0
		for s in summaries:
			if os.path.basename(f).split(os.extsep)[0] in s:
				flag = 1

		if flag == 0:
			unprocessed.extend([f])

	# Organize by newest file
	unprocessed.sort(key=os.path.getctime)

	# No unprocessed files
	if not unprocessed:
		print "No unprocessed files remaining"
		exit()

	# Newest file
	targetFile = unprocessed[-1]

	return targetFile


def main():
	# If process is not running, launch and save PID to file
	if not statusPID(pidFile, args.source):
		# Select file for analyzeFits
		targetFile = getNewest(args.fitsDir, args.sumDir)

		# Launch analyzeFits
		P = subprocess.Popen(['python', args.analyzeFits, targetFile, args.sumDir])
		PID = P.pid

		# Write PID to PID lockfile
		writePID(PID, args.source)
	else:
		logging.info("Process is already running")


if __name__ == '__main__':
	main()




