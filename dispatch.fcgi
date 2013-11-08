#!/home/jbridon/local/bin/python

import sys

from paste.deploy import loadapp
from flup.server.fcgi_fork import WSGIServer

app = loadapp('config:/home/jbridon/corecodex.com/release.ini')
server = WSGIServer(app)
server.run()

