import sys, re, os
sys.path.append('/lsst/home/becker/python/pyfits-1.3/lib/python')
import pyfits
import numpy

def newName(version, type, ccd, amp):
    filename  = '%s-c%03d-a%03d_img.fits' % (type, ccd, amp)
    return os.path.join(version, filename)

def splitCcd(header, data, infile, ccd, rootdir='/lsst/images/repository/input/', isCal=True):
    fields   = infile.split('.')
    version  = fields[0]
    type     = fields[1]
    filter   = fields[2]
    ccddir   = os.path.join(version, str(ccd))

    if not os.path.isdir(version):
        os.mkdir(version)
    #if not os.path.isdir(ccddir):
    #    os.mkdir(ccddir)
    
    # We have to undo whatever imsplice has done
    #
    # HISTORY imsplice: FLIPS ver 2.0 - Elixir by CFHT - Thu Jun 5 2003 - 22:11:29
    # HISTORY imsplice: Splicing the two readouts (A&B) per CCD into a unique image
    # HISTORY imsplice: Splicing results in all detectors as if read from A amplifier
    # HISTORY imsplice: NEXTEND keyword updated (/2) = number of CCDs vs. amplifiers
    # HISTORY imsplice: EXTNAME keyword becomes `ccdxx` instead of `ampxx`
    # HISTORY imsplice: AMPNAME keyword now covers both amplifiers (eg `29a + 29b')
    # HISTORY imsplice: keyword {GAIN, RDNOISE, MAXLIN} replaced by two keywords [A,B]
    # HISTORY imsplice: DATASEC and DETSEC keywords now reflect the entire CCD
    # HISTORY imsplice: BIASSEC becomes irrelevant -> replaced by BSECA & BSECB
    # HISTORY imsplice: New keywords are DETSECA, DETSECB, DSECA, DSECB, TSECA, TSECB
    # HISTORY imsplice: New keywords are ASECA, ASECB, CSECA, CSECB

    # http://cfht.hawaii.edu/Instruments/Imaging/MegaPrime/rawdata.html
    
    # Summary:
    # The CCD images are 2k x 4k.
    # We will chop into CFHT amp images 1k x 4k.
    # And then into LSST amp images 1k x 1k.

    # Details:
    # The CCD images are 2112 by 4644.
    #
    # We ignore the overscan on top (TSA)
    # 
    # A pixels  : 1:1056     1:4612
    # B pixels  : 1057:2112  1:4612
    # note that pyfits convetion is y, x

    cfhtAmpA  = data[:4612, 0:1056]
    cfhtAmpB  = data[:4612, 1056:2112]

    nPixY = 1153
    for i in range(4):
        y0 = i * nPixY
        y1 = y0 + nPixY

        # since they are not trimmed to it here
        lsstAmpA = cfhtAmpA[y0:y1, 32:1056]
        lsstAmpB = cfhtAmpB[y0:y1, 0:(1056-32)]

        #print 'A2', lsstAmpA[0][0]
        #print 'B2', lsstAmpB[0][0]

        headerA  = header.copy()
        headerB  = header.copy()

        # which cfht amp?
        headerA.update('AMPLIST', 'A')
        headerB.update('AMPLIST', 'B')

        # which lsst amp?
        Aid = i + 0
        Bid = i + 4
        headerA.update('LSSTAMP',  Aid)
        headerB.update('LSSTAMP',  Bid)

        # exposure id
        headerA.update('EXPID',  0, 'LSST VISIT')
        headerB.update('EXPID',  0, 'LSST VISIT')

        # DONT FORGET TO RESIZE
        #headerA.update('NAXIS1', lsstAmpA.shape[0])
        #headerB.update('NAXIS1', lsstAmpB.shape[0])
        #headerA.update('NAXIS2', lsstAmpA.shape[1])
        #headerB.update('NAXIS2', lsstAmpB.shape[1])

        if not isCal:
            # reset the appropriate readnoise
            headerA.update('RDNOISE',  headerA['RDNOISEA'])
            headerB.update('RDNOISE',  headerB['RDNOISEB'])
            
            # reset the appropriate gain
            headerA.update('GAIN',  headerA['GAINA'])
            headerB.update('GAIN',  headerB['GAINB'])
            
            # set the appropriate overscan
            headerA.update('BIASSEC', '[1:32,1:%d]'      % (nPixY))
            headerB.update('BIASSEC', '[1025:1056,1:%d]' % (nPixY))
            
            # set the appropriate datasec
            headerA.update('DATASEC', '[33:1056,1:%d]'   % (nPixY))
            headerB.update('DATASEC', '[1:1024,1:%d]'    % (nPixY))
            
            # set the appropriate trimsec
            headerA.update('TRIMSEC',  headerA['DATASEC'])
            headerB.update('TRIMSEC',  headerB['DATASEC'])
            
            # set the appropriate crpix1
            headerA.update('CRPIX1',  headerA['CRPIX1'])
            headerB.update('CRPIX1',  headerB['CRPIX1'] - 1024)
            
            # set the appropriate crpix2
            headerA.update('CRPIX2',  headerA['CRPIX2'] - y0)
            headerB.update('CRPIX2',  headerB['CRPIX2'] - y0)
            
            # EMPERICAL
            # 33 PIXELS IS OVERSCAN SIZE...
            # Maybe its the top overscan that we just got rid of?
            if i > 17:
                headerA.update('CRPIX1',  headerA['CRPIX1'] - 33)
            else:
                headerB.update('CRPIX1',  headerB['CRPIX1'] - 33)

        outfileA = newName(version, type+'-'+filter, ccd, Aid)
        outfileB = newName(version, type+'-'+filter, ccd, Bid)
        print '# Writing', outfileA
        pyfits.PrimaryHDU(lsstAmpA, headerA).writeto(outfileA, output_verify='silentfix', clobber=True)

        maskA = re.sub('_img.fits', '_msk.fits', outfileA)
        lsstAmpA *= 0
        pyfits.PrimaryHDU(lsstAmpA.astype(numpy.int16)).writeto(maskA, clobber=True)

        varA  = re.sub('_img.fits', '_var.fits', outfileA)
        lsstAmpA += 0.1
        pyfits.PrimaryHDU(lsstAmpA).writeto(varA, clobber=True)

        
        print '# Writing', outfileB
        pyfits.PrimaryHDU(lsstAmpB, headerB).writeto(outfileB, output_verify='silentfix', clobber=True)

        maskB = re.sub('_img.fits', '_msk.fits', outfileB)
        lsstAmpB *= 0
        pyfits.PrimaryHDU(lsstAmpB.astype(numpy.int16)).writeto(maskB, clobber=True)

        varB  = re.sub('_img.fits', '_var.fits', outfileB)
        lsstAmpB += 0.1
        pyfits.PrimaryHDU(lsstAmpB).writeto(varB, clobber=True)
    

for infile in sys.argv[1:]:
    ptr          = pyfits.open(infile)
    commonHeader = ptr[0].header

    for i in range(1, 37):
        ccdHeader = ptr[i].header
        ccdData   = ptr[i].data

        # reference image : debugging
        #outfile = 'tmp_%d.fits' % (i)
        #pyfits.PrimaryHDU(ccdData, ccdHeader).writeto(outfile, output_verify='silentfix', clobber=True)
        
        splitCcd(ccdHeader, ccdData, infile, i-1, rootdir='.')
