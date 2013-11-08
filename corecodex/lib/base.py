#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: base.py
# Info: Base controller that all sub-controllers must inherit from.
# This base controller is customized so that we can deal with
# user information / sessions
# 
#################################################################

# Standard includes
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render
from pylons import request, response, session, tmpl_context as c, url

# Base controller
class BaseController(WSGIController):

	def __call__(self, environ, start_response):
	
		# Update the user header information (Content found on the very top-right of the GUI)
		self.BaseController_UpdateUserHeader()
		
		"""Invoke the Controller"""
		# WSGIController.__call__ dispatches to the Controller method
		# the request is routed to. This routing information is
		# available in environ['pylons.routes_dict']
		return WSGIController.__call__(self, environ, start_response)

	# Updates the header information for the context / mako template
	def BaseController_UpdateUserHeader(self):
	
		# Is the user already logged-in?
		if session.get("UserName"):
			
			# User info
			c.user_login = "Log Out"
			c.user_loginurl = "logout"
			c.user_pref = "Preferences"
			c.user_prefurl = "preferences"
			c.user_name = session.get("UserName")
			c.user_points = session.get("UserPoints")
			c.user_icon = session.get("UserIconID")
			c.is_admin = session.get("IsAdmin")
		
		# Nope! Default to basic URLs
		else:
			
			# User info
			c.user_login = "Log In"
			c.user_loginurl = "login"
			c.user_pref = "Register"
			c.user_prefurl = "register"
			c.user_name = ""
			c.user_points = 0
			c.user_icon = 0
			c.is_admin = False
		
		# Top-bar directory info
		c.group_name = ""
		c.group_id = -1
		c.challenge_name = ""
		c.challenge_id = -1

