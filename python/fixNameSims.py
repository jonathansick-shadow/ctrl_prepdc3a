import pyfits
import os, re
import sys

for file in sys.argv[1:]:
    fields = file.split('/')
    date = fields[0]
    exp  = fields[1]
    badstr = 'e%03d'%(int(exp)) + date[-3:]
    newstr = '%s-e%03d' % (date, int(exp))
    newname = re.sub(badstr, newstr, file)
    os.rename(file, newname)
    print file, newname
