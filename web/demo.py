import os,sys

# Add the current dir (web) to sys.path
sys.path = [os.path.dirname(os.path.realpath(__file__))] + sys.path

# Add fabicon lib path to sys.path
sys.path = [os.path.dirname(os.path.realpath(__file__)) + '/../'] + sys.path

# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))

import bottle
import fabiconweb

application = bottle.default_app()
bottle.run(application, host='localhost', port=8080)

