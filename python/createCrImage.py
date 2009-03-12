import sys, re
import lsst.afw.image as afwImage
import lsst.afw.math as afwMath

def addCosmicRays(image, nCR=100, emin=100, emax=1000):
    seed = int(afwMath.makeStatistics(image, afwMath.MAX).getValue())
    if seed == 0:
        seed = 1

    width = image.getWidth()
    height = image.getHeight()

    rand = afwMath.Random(afwMath.Random.RANLUX, seed)

    for i in range(nCR):
        #
        # Initial point in CR
        #
        x = rand.uniformInt(width)
        y = rand.uniformInt(height)
        amp = emin + rand.uniformInt(emax - emin)

        badPixels = []
        while True:
            badPixels.append([x, y, amp + 0.1*(emax - emin)*rand.uniform()])

            if rand.uniform() > 0.5:
                break

            x += rand.uniformInt(3) - 1
            y += rand.uniformInt(3) - 1

        for x, y, amp in badPixels:
            if x >= 0 and x < width and y >= 0 and y < height:
                image.set(x, y, amp)

            while rand.uniform() < 0.1:
                image.set(x, y, (emax - emin)*rand.uniform())

                x += rand.uniformInt(3) - 1
                y += rand.uniformInt(3) - 1

            for x, y, amp in badPixels:
                if x >= 0 and x < width and y >= 0 and y < height:
                    image.set(x, y, amp)


for inputfile in sys.argv[1:]:
    imc       = afwImage.ImageF(inputfile)
    addCosmicRays(imc)
    outfile = re.sub('/0/', '/1/', inputfile)
    outfile = re.sub('e000', 'e001', outfile)

    fields = inputfile.split('/')
    os.path.mkdir( os.path.join(fields[0], '1') )
    
    imc.writeFits( outfile )
    
