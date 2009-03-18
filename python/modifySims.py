import pyfits, sys
import numpy as num

# teh sims have negative values in teh overscan.  fix this.
for file in sys.argv[1:]:
    ptr = pyfits.open(file,  mode='update')
    ptr[0].data = num.abs(ptr[0].data)
    ptr.flush()
        
