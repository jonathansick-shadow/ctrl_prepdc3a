import os
import re
import sys

# raw images are going to be called :
# visit/exposure/ccd/amp*.fits


def newName(visit, exposure, ccd, amp):
    directory = os.path.join(str(visit), str(exposure))
    filename = 'raw-%06d-e%03d-c%03d-a%03d.fits' % (visit, exposure, ccd, amp)

    return os.path.join(directory, filename)


def doRename(string):
    fields = string.split('/')

    visit = int(re.sub('o', '', fields[0]))
    print 'mkdir %s' % (visit)
    ccd = int(fields[1]) - 1  # for CFHT
    print 'mkdir %s' % (os.path.join(str(visit), str(ccd)))

    fields = fields[2].split('_')
    amp = int(fields[-1][0])

    rename = newName(visit, 0, ccd, amp)
    print 'mv %s %s' % (string, rename)

for file in sys.argv[1:]:
    doRename(file)
