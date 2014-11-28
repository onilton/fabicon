import os,sys

# Changing sys.path to allow including local libraries and .py

# Add the current dir (web) to sys.path
sys.path = [os.path.dirname(os.path.realpath(__file__))] + sys.path

# Add fabicon lib path to sys.path
sys.path = [os.path.dirname(os.path.realpath(__file__)) + '/../'] + sys.path

#print "sys.path",sys.path

# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))

#sys.stdout = sys.stderr # for debugging only
#print "sys.path",sys.path
#print "os.path",os.path.dirname(__file__)

import bottle
import fabiconweb
# ... build or import your bottle application here ...
# Do NOT use bottle.run() with mod_wsgi
application = bottle.default_app()

