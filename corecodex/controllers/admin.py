#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: admin.py
# Info: Administrative / group management
# 
#################################################################

# Standard includes
import logging
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from corecodex.lib.base import BaseController, render

log = logging.getLogger(__name__)

# The administration controller
class AdminController(BaseController):
	
	
	# Returns true if the current user is an administrator
	# For now, we just check cookies; in the future we should check against the DB
	# since someone might be left logged in but have their admin-privlidges revoked
	def IsAdmin(self):
		if session.get("IsAdmin") == True:
			return True
		else:
			return False
	
	
	# Root page for administration
	def admin(self):
	
		# Check for page permission
		if not self.IsAdmin():
			abort(status_code = 403, detail = "Forbidden: You are not an administrator.")
		
		# Render the admin page if the user has rights...
		c.body_content = render("/content_admin.html")
		return render("/theme.html")
