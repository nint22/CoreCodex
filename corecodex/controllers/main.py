#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: main.py
# Info: Main controller / landing page for the site without accessing
# any specific page...
# 
#################################################################

# Standard includes
import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from corecodex.lib.base import BaseController, render

# Start logging..
log = logging.getLogger(__name__)

# Main controller class
class MainController(BaseController):
	
	# Standard main response
    def index(self):
        
        # Render the main theme with the default main content
        c.body_content = render("/content_splash.html")
        return render("/theme.html")
		