#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: error.py
# Info: Error page / error handler controller.
#
#   Original Doc:
# 
#   The ErrorDocuments middleware forwards to ErrorController when error
#   related status codes are returned from the application.
# 
#   This behaviour can be altered by changing the parameters to the
#   ErrorDocuments middleware in your config/middleware.py file.
# 
#################################################################

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from corecodex.lib.base import BaseController, render

from paste.urlparser import PkgResourcesParser
from pylons.middleware import error_document_template
from webhelpers.html.builder import literal

from corecodex.lib.base import BaseController

class ErrorController(BaseController):
	
	# Load regular doc
	def document(self):
		
		# Get some basic error information
		resp = request.environ.get('pylons.original_response')
		exception = request.environ.get('pylons.controller.exception')
		
		# If no exception, just post the original message
		if not exception:
			c.error_description = resp.status
		
		# Post error code and description (Just a combined string)
		else:
			c.error_description = str(resp.status_int) + " - " + str(exception.detail)
		
		# Load the about page content and then post it
		# back through the standard renderer
		c.body_content = render("/content_error.html")
		return render("/theme.html")
		
		#request = self._py_object.request
		#resp = request.environ.get('pylons.original_response')
		#content = literal(resp.body) or cgi.escape(request.GET.get('message', ''))
		#page = error_document_template % \
		#    dict(prefix=request.environ.get('SCRIPT_NAME', ''),
		#         code=cgi.escape(request.GET.get('code', str(resp.status_int))),
		#         message=content)
		#return page
