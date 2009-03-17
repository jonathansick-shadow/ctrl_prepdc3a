import sys, re, os
import pyfits, numpy

for calib in sys.argv[1:]:
    img  = re.sub('.fits', '_img.fits', calib)
    data = pyfits.open(calib)[0].data
    
    mask = re.sub('.fits', '_msk.fits', calib)
    data *= 0
    pyfits.PrimaryHDU(data.astype(numpy.int16)).writeto(mask, clobber=True)

    var = re.sub('.fits', '_var.fits', calib)
    data += 0.1
    pyfits.PrimaryHDU(data).writeto(var, clobber=True)

    cmd  = 'mv %s %s' % (calib, img)
    print cmd
    os.system(cmd)
