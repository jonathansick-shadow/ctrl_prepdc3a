import os, re

# raw images are going to be called :
# visit/exposure/ccd/amp*.fits

def newName(visit, exposure, ccd, amp):
    directory = os.path.join(str(visit), str(exposure))
    filename  = 'raw-%06d-e%03d-c%03d-a%03d.fits' % (visit, exposure, ccd, amp)

    return os.path.join(directory, filename)

def doRename(string):
    fields = '/'.split(string)

    visit  = int(re.sub('o', '', fields[0]))
    print 'mkdi %s' % (visit)
    ccd    = int(fields[1])
    print 'mkdir %s' % (os.path.join(visit, ccd))

    for amp in range(1,8):
        rename = newName(visit, 0, ccd, amp-1)
        print 'mv %s %s' % (string, rename)

for file in sys.argv[1:]:
    doRename(file)
