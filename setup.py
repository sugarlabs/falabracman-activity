#!/usr/bin/env python
try:
   from sugar3.activity import bundlebuilder
   bundlebuilder.start()
except ImportError:
   import os
   os.system("find ./ | grep -v .svn | grep -v '.pyc$' | sed 's,^./,falabracman.activity/,g' > MANIFEST")
   os.chdir('..')
   os.system('rm falabracman.xo')
   os.system('cat falabracman.activity/MANIFEST | zip falabracman.xo -@')
   #os.system('mv falabracman.xo ./falabracman.activity')
   os.chdir('falabracman.activity')
