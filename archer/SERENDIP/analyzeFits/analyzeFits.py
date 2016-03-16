"""
Analyzes and summarizes FITS file data

Use: Python analyzeFits.py <filename> <output directory>
"""

import os
import sys
import time
from datetime import datetime
import numpy as np
import matplotlib; matplotlib.use('Agg') # Must be called before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages # Save plots to PDF
import matplotlib.cm as cm
from pyPdf import PdfFileWriter, PdfFileReader# Merge PDF pages
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter #, landscape
import json
import logging
import fitsio
import argparse


# Parameters
tStep = 1.43

# Arguments
parser = argparse.ArgumentParser(description="Summarizes FITS data as PDF")
parser.add_argument('filepath', help="Path to fits file")
parser.add_argument('outDir', help="Desired output directory")
parser.add_argument('--level', help="Set logging level, see logging module for help",
                    default='WARNING')
args = parser.parse_args()

# Logging
logLevel = getattr(logging, args.level.upper())
logging.basicConfig(level=logLevel)


class fitsData:

    def __init__(self, filepath):
        """
        Processes data from FITS file
        """

        with fitsio.FITS(filepath) as fileHandle:
            # Parse data
            ETHITS, CCPWRS, rows, times = [[] for i in range(4)]
            step = -1
            delim = ['GBTSTATUS', 'AOSCRAM'] # Tables delimiting timesteps
            # It might be tempting to seperate this, but doing this all at once
            # Is faster as it limits the amount of times the filehandle is used
            for HDU in fileHandle:
                try:
                    if any(elem in HDU.read_header()['EXTNAME'] for elem in delim):
                        step += 1
                    elif 'ETHITS' in HDU.read_header()['EXTNAME']:
                        ETHITS.append(HDU.read())

                        # Row form for plotting vs time
                        for row in HDU.read():
                            times.append(tStep * step)
                            if row[2] == 0:
                                rows.append(row[3])
                            else:
                                rows.append(row[2]*2**19 + row[3])
                    elif 'CCPRWS' in HDU.read_header()['EXTNAME']:
                        CCPWRS.append(HDU.read())
                except ValueError: # EXTNAME not in header
                    pass

            self.ETHITS = ETHITS # Columns: DETPOW, MEANPOW, COARCHAN, FINECHAN
            self.finePoints = zip(rows, times) # Fine channel vs time
            self.CCPWRS = CCPWRS
            self.meta = {
                        'FILENAME': filename,
                        'NHITS': len(rows),
                        'TIME': fileHandle[0].read_header()['DATE'],
                        'NSTEPS': step,
                        'DURATION_MIN': str(round((tStep*step)/60, 2)),
                        'FILE SIZE_MB': str(round(os.stat(filepath).st_size/(1024.0**2), 2)),
                        'COARSEID': fileHandle[1].read_header()['COARCHID']
                        }

def plotPDF(data):
    """
    Prints plots to PDF
    """
    
    def powerHist(data):
        """
        Plots number of hits occured at each power level
        """

        # Get DETPOW/MEANPOW
        relpow = [row[0]/row[1] for table in data.ETHITS for row in table if row[1] != 0]

        # Plot histogram
        plt.figure()
        plt.hist(relpow, bins = 1e3) # arbitrary bin amount
        plt.title('Power Histogram')
        plt.xlabel('Relative Power (DETPOW/MEANPOW)')
        plt.ylabel('Number of Hits')
        plt.autoscale(enable=True, axis='x', tight=True)
        plt.yscale('log', nonposy='clip')
        # plt.show(block = False)

    def coarseHist(data):
        """
        Plots the number of hits occured in each bin
        """

        # Get COARSCHAN
        coarse = [data.meta['COARSEID'] + row[2] for table in data.ETHITS for row in table]

        # Plot histogram
        plt.figure()
        plt.hist(coarse, bins = 1e3) # arbitrary bin amount
        plt.title('Coarse Bin Histogram')
        plt.xlabel('Coarse Bin Number')
        plt.ylabel('Number of Hits')
        plt.autoscale(enable=True, axis='x', tight=True)
        plt.yscale('log', nonposy='clip')

    def coarseSpectrum(data):
        """
        Plots power in each coarse channel (pole)
        """

        # Get powers
        xpol, ypol = [[row[0], row[1]] for table in data.CCPWRS for row in table]

        # Plot histogram
        plt.figure()
        plt.plot(xpol[0:512], '-r', label = 'XPOL')
        plt.plot(ypol[0:512], '-b', label = 'YPOL')
        plt.title('Coarse Spectrum')
        plt.legend(loc = 'center right')
        plt.xlabel('Coarse Bin Number')
        plt.autoscale(enable=True, axis='x', tight=True)
        plt.ylabel('Power')
        plt.yscale('log')

    def waterfallHits(data):
        """
        Plots the time at which a signal was received vs its frequency
        """

        # Plot waterfall
        plt.figure()
        plt.plot(*zip(*data.finePoints), rasterized=True, linestyle='', color='black', marker='o', markersize=1)
        plt.title('Waterfall Hits')
        plt.xlabel('Fine Channel Number (Starting at channel ID)')
        plt.ylabel('Time (s)')
        plt.autoscale(enable=True, axis='x', tight=True)
        plt.ylim(ymin=0)

    def waterfallCoarse(data):
        """
        Plots CCPWRS over time. Color indicates Power.
        """

        # Plot xpol waterfall
        plt.figure()
        plt.figure(figsize=(10,10))
        plt.subplot(2,1,1)
        xpol = [row[0] for table in data.CCPWRS for row in table]
        imgX = np.array(xpol)
        imgX = imgX.reshape(len(ccpwrs),512)
        plt.imshow(imgX.astype(int), origin='lower', aspect='auto', cmap = cm.hot)
        plt.title('X-Pole CCPWRS')
        plt.ylabel('No. Time Steps (Time/Time Step)')
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.xlabel('Coarse Channel ID')

        # Plot ypol waterfall
        plt.subplot(2,1,2)
        ypol = [row[1] for table in data.CCPWRS for row in table]
        imgY = np.array(ypol)
        imgY = imgY.reshape(len(ccpwrs),512)
        plt.imshow(imgY.astype(int), origin='lower', aspect='auto', cmap = cm.hot)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.title('Y-Pole CCPWRS')
        plt.ylabel('No. Time Steps (Time/Time Step)')
        plt.xlabel('Coarse Channel ID')
        plt.subplots_adjust(hspace=0.4)

    # Create PDF
    pdf = PdfPages('%s_plots.pdf' %(os.path.join(outDir, os.path.splitext(filename)[0])))
    
    # Generate plots and save to PDF
    powerHist(data); pdf.savefig(); plt.close()
    coarseHist(data); pdf.savefig(); plt.close()
    waterfallHits(data); pdf.savefig(); plt.close()
    if data.CCPWRS:
        waterfallCoarse(data); pdf.savefig(); plt.close()
    # Close PDF and figures
    pdf.close()
    plt.close('all') # Just to be sure

def metaSummary(data, outDir):
    """
    Prints meta data to cover page as a summary of the FITS file
    """

    def drawPage(meta):
        """
        Creates cover page
        """

        def coverPage(canvas, doc):
            """
            Cover page format
            """
            canvas.saveState()
            canvas.setFont('Times-Bold',16)
            canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
            canvas.setFont('Times-Roman',9)
            canvas.restoreState()

        # PDF Parameters
        PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
        styles = getSampleStyleSheet()
        Title = 'FITS Summary'

        # Create cover page
        doc = SimpleDocTemplate('%s_meta.pdf' %(os.path.join(outDir, os.path.splitext(filename)[0])))
        content = [Spacer(1,2*inch)]
        style = styles["Normal"]
        for key in sorted(meta.keys()):
            text = ("%s: %s \n" % (key, meta[key]))
            p = Paragraph(text, style)
            content.append(p)
        doc.build(content, onFirstPage = coverPage)

    def jsonMeta(meta, outDir):
        """
        Saves metadata to txt file using json
        """

        def jsonImport(jsonPath):
            """
            Retrieves stored data. Creates file if none found.
            """

            # Get stored data from log file
            try:
                with open(jsonPath) as infile:
                    jsonData = json.load(infile)
            except:
                # New file will be created with jsonExport
                jsonData = {}

            return jsonData

        def jsonExport(jsonPath, jsonData):
            """
            Exports data to txt file using json
            """

            with open(jsonPath, 'wb') as outfile:
                json.dump(jsonData, outfile, sort_keys=True, indent=4, separators=(',', ': '))

        def jsonAdd(jsonData, data):
            """
            Adds new data to stored json data
            """

            # Year-week time stamp
            digits = [i for i in filename.split('_') if i.isdigit() and len(i) == 8]
            if len(digits) > 1:
                for i in digits:
                    if i[1:2] == '20':
                        # Assuming that odds are that this will be correct
                        digits = i
            else:
                digits = digits[0]

            timeStamp = '%s %s %s' % (digits[0:4], digits[4:6], digits[6:8])
            timeStamp = datetime.strptime(timeStamp, '%Y %m %d')

            week = timeStamp.timetuple().tm_yday/7 + 1
            year = timeStamp.year
            timeKey = str(year)+'-'+str(week)

            # Create year-week entry if doesnt exist
            jsonData[timeKey] = jsonData.get(timeKey) or {}

            jsonData[timeKey]['DURATION_MIN'] = jsonData.get(timeKey).get('DURATION_MIN', 0) + \
                float(data.meta['DURATION_MIN'].split()[0])

            return jsonData

        # Summary file location
        jsonPath = os.path.join(outDir,'summary.txt')

        # Append new data
        jsonData = jsonImport(jsonPath)
        jsonData = jsonAdd(jsonData, data)

        # Save data to summary file
        jsonExport(jsonPath, jsonData)

        return True

    jsonMeta(data.meta, outDir)
    drawPage(data.meta) # Creates summary page

    return True
    

def pdfMerge():
    """
    Merges generated PDFs into one called <filename>_summary
    Deletes the individual consituent PDFs
    """

    def append_pdf(input, output):
        """
        Combines PDF pages to be  merged
        """

        [output.addPage(input.getPage(page_num)) for page_num in range(input.numPages)]

    # Merge PDFs
    output = PdfFileWriter()
    append_pdf(PdfFileReader(file('%s_meta.pdf' %(os.path.join(outDir, os.path.splitext(filename)[0])), 'rb')), output)
    append_pdf(PdfFileReader(file('%s_plots.pdf' %(os.path.join(outDir, os.path.splitext(filename)[0])), 'rb')), output)

    outputFile = file('%s_summary.pdf' %(os.path.join(outDir, os.path.splitext(filename)[0])), 'wb')
    output.write(outputFile)
    outputFile.close()

    # Delete PDFs
    os.remove('%s_plots.pdf' %(os.path.join(outDir, os.path.splitext(filename)[0])))
    os.remove('%s_meta.pdf' %(os.path.join(outDir, os.path.splitext(filename)[0])))

def main():
    """
    Summarizes and analyzes FITS file
    """

    logging.info('Filename: %s' %filename)
    logging.info('Output dir: %s' %outDir)

    logging.info('Parsing Data, this may take a few minutes')
    data = fitsData(filepath)

    logging.info('Printing Metadata to PDF')
    metaSummary(data, outDir)

    logging.info('Plots printing to PDF, this may take a while')
    plotPDF(data)

    logging.info('Merging files and cleaning up')
    pdfMerge()

    logging.info('Done')


if __name__ == "__main__":
    start = time.time()
    logging.info('Starting timer')


    filepath = sys.argv[1]
    fileDir, filename = os.path.split(filepath)
    filename = os.path.splitext(filename)[0]
    outDir = os.path.abspath(os.path.expanduser(sys.argv[2]))
    if os.path.isdir(outDir) == False:
        sys.exit('Exiting: Output directory does not exist')

    main()


    logging.info('Total Time: %d Seconds' %(time.time()-start))
