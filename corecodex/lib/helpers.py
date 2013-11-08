#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: helpers.py
# Info: Series of global functions used globally as "helper" functions
# most commonly used for theming and formatting support
# 
#################################################################

# Standard includes..
from webhelpers.html import literal
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pylons import tmpl_context as c

# Global string whitelist that we find commonly helpul
string_whitespaces = " \a\b\f\n\r\t\v"
string_whitelist = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-@."
string_whitelist_password = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`~!@#$%^&*()_-+=\\|[]{};':\",./<>?"

# Whitelist characters string check
# Returns true if the given string only contains characters
# of the second given string
def string_check_whitelist(source, whitelist):
	
	valid_string = True
	
	for source_char in source:
		# Not found - thus it is not in the whitelist
		if whitelist.find(source_char) < 0:
			valid_string = False
			break
	
	return valid_string


# Given source code, and a language, convert it into HTML that can render out
# directly onto the browser screen. Returns the original source code upon failure
# Note, as degined in the "lib/Challenges.py" source file, we map out languages by the
# following names:
# p, py, python -> Python
# c, c89, c99 -> GCC C
# cp, cpp, c++ -> C++
# j, java -> Java
def code_to_html(SourceCode, SourceLanguage):
	
	# To lower the source language
	SourceLanguage = SourceLanguage.lower()
	
	# Convert language directly to python
	if SourceLanguage == "python":
		
		# Generate the required CSS header
		Formatter = HtmlFormatter(linenos=True, cssclass="source")
		
		# Generate the formatted code
		FormattedCode = highlight(SourceCode, PythonLexer(), Formatter)
		
		# Force the block of source code "pre" tag tage the page width
		FormattedCode = FormattedCode.replace('<td class="code">', '<td class="code" width="100%">')
		
		# Return a web-friendly string
		return literal(FormattedCode)
		
	# Unsupported language
	else:
		c.pygments_css_header = ""
		return literal("<pre>") + SourceCode + literal("</pre>")

