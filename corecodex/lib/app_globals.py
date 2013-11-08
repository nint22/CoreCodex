#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: app_globals.py
# Info: The application's global objects (note this is a single-instaince
# object)
# 
#################################################################

# Standard includes
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from pygments.formatters import HtmlFormatter
from pylons import config

# Globals class
class Globals(object):
	
	# Setup the application's environment global
	version_description = "Alpha (0.7)"
	
	# Called during application initialization
	def __init__(self, config):
		self.cache = CacheManager(**parse_cache_config_options(config))
	