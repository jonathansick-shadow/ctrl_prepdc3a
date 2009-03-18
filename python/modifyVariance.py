import pyfits, sys
import numpy as num

# give the cals zero variance
for file in sys.argv[1:]:
    if not file.endswith('_var.fits'):
        continue
    ptr = pyfits.open(file,  mode='update')
    ptr[0].data = 0.0 * ptr[0].data
    ptr.flush()
