import pyfits
import lsst.ip.isr as ipIsr
import lsst.afw.image as afwImage
import lsst.afw.detection as afwDetection
import sys, os, re
import lsst.afw.display.ds9 as ds9

rootdir  = '.'
infile   = sys.argv[1]
basename = re.sub('.fits', '', os.path.basename(infile))
basedir  = os.path.join(rootdir, basename)
if not os.path.isdir(basedir):
    os.mkdir(basedir)

ptr    = pyfits.open(infile)
for i in range(1, 37):
    raftdir  = os.path.join(basedir, str(i))
    if not os.path.isdir(raftdir):
        os.mkdir(raftdir)
        
    ccdHeader = ptr[i].header
    nColMask  = ccdHeader['NAXIS1']
    nRowMask  = ccdHeader['NAXIS2']
    mask      = afwImage.MaskU(nColMask, nRowMask)
    mask.set(0)
    
    bitmask = mask.getPlaneBitMask('BAD')
    print bitmask
    for card in ccdHeader.ascardlist().keys():
        if card.startswith('MASK_'):
            datasec = ccdHeader[card]
            print datasec
            bbox    = ipIsr.BboxFromDatasec(datasec)
            print type(bbox)
            print bbox.getX0(), bbox.getX1(), bbox.getY0(), bbox.getY1()
            fp      = afwDetection.Footprint(bbox)
            print fp.getBBox().getX0(), fp.getBBox().getX1(), fp.getBBox().getY0(), fp.getBBox().getY1()
            
            afwDetection.setMaskFromFootprint(mask, fp, bitmask)
            break

    outfile0 = '%d.fits' % (i)
    print '# Writing', outfile0
    mask.writeFits(outfile0)
    
    bboxA = afwImage.BBox(afwImage.PointI(0,0),
                          afwImage.PointI(1055,4611))
    bboxB = afwImage.BBox(afwImage.PointI(1056,0),
                          afwImage.PointI(2111,4611))

    cfhtAmpA  = afwImage.MaskU(mask, bboxA)
    cfhtAmpB  = afwImage.MaskU(mask, bboxB)

    #print cfhtAmpA.getDimensions()
    #print cfhtAmpB.getDimensions()

    # copied from stageCfhtForDc3a
    nPixY = 1153
    for i in range(4):
        y0 = i * nPixY
        y1 = y0 + nPixY - 1

        bbox = afwImage.BBox(afwImage.PointI(0,y0),
                             afwImage.PointI(1055,y1))
        #print bbox.getX0(), bbox.getX1(), bbox.getY0(), bbox.getY1()
        lsstAmpA = afwImage.MaskU(cfhtAmpA, bbox)
        lsstAmpB = afwImage.MaskU(cfhtAmpA, bbox)

        #print lsstAmpA.getDimensions()
        #print lsstAmpB.getDimensions()

        Aid = i + 1
        Bid = i + 5

        outfileA = os.path.join(raftdir, '%s_%d_%s.fits' % (basename, i, Aid))
        outfileB = os.path.join(raftdir, '%s_%d_%s.fits' % (basename, i, Bid))
        print '# Writing', outfileA
        lsstAmpA.writeFits(outfileA)
        print '# Writing', outfileB
        lsstAmpB.writeFits(outfileB)
        
        
