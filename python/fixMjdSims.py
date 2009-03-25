import pyfits
import os
import sys

for file in sys.argv[1:]:
    ptr    = pyfits.open(file, mode='update')
    header = ptr[0].header

    mjd = header['MJD-OBS'] - 2400000.5
    #print file, header['MJD-OBS'], mjd
    header['MJD-OBS'] = mjd
    header.update('FILENAME', os.path.basename(file))
    header.update('SATURATE', 65535.)
    ptr.flush()
