


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
                    elif 'CCPWRS' in HDU.read_header()['EXTNAME']:
                        CCPWRS.append(HDU.read())
                except ValueError: # EXTNAME not in header
                    pass

            self.ETHITS = ETHITS # Columns: DETPOW, MEANPOW, COARCHAN, FINECHAN
            self.finePoints = zip(rows, times) # Fine channel vs time
            self.CCPWRS = CCPWRS
            self.nSteps = step
            self.coarseID = fileHandle[1].read_header()['COARCHID']






