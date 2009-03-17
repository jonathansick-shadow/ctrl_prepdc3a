import pyfits
import lsst.afw.image as afwImage
import lsst.afw.detection as afwDetection
import sys, os, re
import lsst.afw.display.ds9 as ds9
import lsst.afw.detection.utils as afwDetectionUtils

def MaskPolicyFromImage(fitsfile, policyfile):
    # input bad pixel image
    maskImage   = afwImage.ImageF(fitsfile)

    # turn into masked image for detection
    maskedImage = afwImage.MaskedImageF(maskImage)

    # find bad regions
    thresh    = afwDetection.Threshold(0.5)
    ds        = afwDetection.DetectionSetF(maskedImage, thresh)
    fpList    = ds.getFootprints()

    buff = open(policyfile, 'w')
    buff.write('#<?cfg paf policy ?>\n')
    buff.write('# Bad pixels for CFHT image %s\n' % (fitsfile))
    buff.write('# Coordinates are for untrimmed image\n')
    
    for i in range(fpList.size()):
        afwDetectionUtils.writeFootprintAsDefects(buff, fpList[i])
    buff.close()
    

rootdir  = '.'
infile   = sys.argv[1]
basename = re.sub('.fits', '', os.path.basename(infile))
basedir  = os.path.join(rootdir, basename)
if not os.path.isdir(basedir):
    os.mkdir(basedir)

maskFormat = re.compile('^\[(\d+):(\d+),(\d+):(\d+)\]$')

ptr    = pyfits.open(infile)
for i in range(1, 37):
    #raftdir  = os.path.join(basedir, str(i))
    #if not os.path.isdir(raftdir):
    #    os.mkdir(raftdir)
        
    ccdHeader = ptr[i].header
    nColMask  = ccdHeader['NAXIS1']
    nRowMask  = ccdHeader['NAXIS2']
    mask      = afwImage.MaskU(nColMask, nRowMask)
    mask.set(0)
    
    bitmask = mask.getPlaneBitMask('BAD')
    for card in ccdHeader.ascardlist().keys():
        if card.startswith('MASK_'):
            datasec = ccdHeader[card]

            # Unfortunately, the format of the masks is wrong.  Its
            # x0,y0  x1,y1
            # e.g.
            # MASK_000= '[1:1,2112:1]'       / Bad pixels area definition
            #
            # Datasecs normally have
            # x0,x1  y0,y1
            # e.g.
            # CCDSIZE = '[1:2048,1:4612]'    / Detector imaging area size
            # bbox    = ipIsr.BboxFromDatasec(datasec)

            match = maskFormat.match(datasec)
            if match == None:
                # unable to match mask area!
                print '# WARNING: Extn', nExt, 'unable to parse', maskArea
                continue
            group = map(int, match.groups())

            # ACB : by visual inspection, the y0 values can be too
            # high by 1.  however, since some of the y0 values are '1'
            # in the mask string, i can't decrement this by 2 without
            # going off the image.  we just deal with this for dc3a.
            bbox  = afwImage.BBox(afwImage.PointI(group[0]-1, group[1]-1),
                                  afwImage.PointI(group[2]-1, group[3]-1))
            
            fp      = afwDetection.Footprint(bbox)
            afwDetection.setMaskFromFootprint(mask, fp, bitmask)

    # debugging
    #outfile0 = '%d.fits' % (i)
    #print '# Writing', outfile0
    #mask.writeFits(outfile0)

    # trim this thing!  it includes the overscan etc...
    
    bboxA = afwImage.BBox(afwImage.PointI(32,0),
                          afwImage.PointI(1055,4611))

    bboxB = afwImage.BBox(afwImage.PointI(1055,0),
                          afwImage.PointI(2111-32,4611))

    #bboxA = afwImage.BBox(afwImage.PointI(0,0),
    #                      afwImage.PointI(1055,4611))

    #bboxB = afwImage.BBox(afwImage.PointI(1056,0),
    #                      afwImage.PointI(2111,4611))

    cfhtAmpA  = afwImage.MaskU(mask, bboxA)
    cfhtAmpB  = afwImage.MaskU(mask, bboxB)

    # copied from stageCfhtForDc3a
    nPixY = 1153
    for j in range(4):
        y0 = j * nPixY
        y1 = y0 + nPixY - 1

        bbox = afwImage.BBox(afwImage.PointI(0,y0),
                             afwImage.PointI(1023,y1))
        
        lsstAmpA = afwImage.MaskU(cfhtAmpA, bbox)
        lsstAmpB = afwImage.MaskU(cfhtAmpA, bbox)

        Aid = j + 0
        Bid = j + 4

        # debugging
        outfileA = os.path.join(basedir, 'defect-c%03d-a%03d.fits' % (i-1, Aid)) # %s_%d_%s.fits' % (basename, i, Aid))
        outfileB = os.path.join(basedir, 'defect-c%03d-a%03d.fits' % (i-1, Bid)) #'%s_%d_%s.fits' % (basename, i, Bid))
        print '# Writing', outfileA
        lsstAmpA.writeFits(outfileA)
        print '# Writing', outfileB
        lsstAmpB.writeFits(outfileB)

        #policyA = os.path.join(raftdir, '%s_%d_%s.paf' % (basename, i, Aid))
        #policyB = os.path.join(raftdir, '%s_%d_%s.paf' % (basename, i, Bid))
        policyA = os.path.join(basedir, 'defect-c%03d-a%03d.paf' % (i-1, Aid))
        policyB = os.path.join(basedir, 'defect-c%03d-a%03d.paf' % (i-1, Bid))

        MaskPolicyFromImage(outfileA, policyA)
        MaskPolicyFromImage(outfileB, policyB)



        
        
        
        
