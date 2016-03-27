import re
import sys
import lsst.afw.image as afwImage

# The cals are all for the untrimmed science data.
# They need to be trimmed.

for img in sys.argv[1:]:
    root = re.sub('_img.fits', '', img)

    exp = afwImage.ExposureF(root)
    metadata = exp.getMetadata()
    amp = metadata.get('LSSTAMP')

    mi = exp.getMaskedImage()
    height = mi.getHeight()
    width = mi.getWidth()

    # don't double-trim!
    if (width == 1024) and (height == 1153):
        print '# skipping', img
        continue

    if amp < 4:
        bbox = afwImage.BBox(afwImage.PointI(32, 0),
                             afwImage.PointI(1055, 1152))

    else:
        bbox = afwImage.BBox(afwImage.PointI(0, 0),
                             afwImage.PointI(1055-32, 1152))

    subexp = afwImage.ExposureF(exp, bbox)
    subexp.getMetadata().combine(exp.getMetadata())
    # overwrite originals; gulp!
    subexp.writeFits(root)

