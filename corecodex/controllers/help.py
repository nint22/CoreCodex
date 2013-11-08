#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: help.py
# Info: Help page forwards - this basically just forwards help or
# help-related queries to the appropriate public content
# 
#################################################################

# Standard includes
import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from corecodex.lib.base import BaseController, render
import corecodex.lib.Achievements as Achievements

# Logging...
log = logging.getLogger(__name__)

# Help forward class
class HelpController(BaseController):
	
	
	# About page
	def about(self):
	
		# Load the about page content and then post it
		# back through the standard renderer
		c.body_content = render("/content_about.html")
		return render("/theme.html")
	
	
	# Contact page
	def contact(self):
		c.body_content = render("/content_contact.html")
		return render("/theme.html")
	
	
	# License page
	def license(self):
		c.body_content = render("/content_license.html")
		return render("/theme.html")
	
	
	# Policy page
	def policy(self):
		c.body_content = render("/content_policy.html")
		return render("/theme.html")
	
	
	# Help page
	def help(self):
		c.body_content = render("/content_help.html")
		return render("/theme.html")
	
	
	# Achievements page
	def achievements(self):
		c.achievements = Achievements.AchievementsQueryAll()
		c.body_content = render("/content_achievements.html")
		return render("/theme.html")

