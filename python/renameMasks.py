import sys, os

indir = sys.argv[1]
for dir in os.listdir(indir):
    ccddir = os.path.join(indir, dir)

    for mask in os.listdir(ccddir):
        if mask.endswith('.fits'):
            os.unlink(os.path.join(ccddir, mask))
        if mask.endswith('.paf'):
            fields = mask.split('_')
            root   = fields[0].split('.')[0]
            ccd    = int(fields[1]) - 1
            amp    = int(fields[2].split('.')[0]) - 1

            #print root, ccd, amp
            #defects-c001-a001.paf
            if not os.path.isdir(root):
                os.mkdir(root)
            outfile = 'defect-c%03d-a%03d.paf' % (ccd, amp)
            infile  = os.path.join(ccddir, mask)
            outfile = os.path.join(root, outfile)
            #print infile, outfile
            os.rename(infile,outfile)
