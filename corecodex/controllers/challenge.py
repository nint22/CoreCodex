#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: challenge.py
# Info: Challenge view controller; used for single-challenge views
# 
#################################################################

# Standard includes
import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from corecodex.lib.base import BaseController, render
import corecodex.lib.Challenges as Challenges
import corecodex.lib.Solutions as Solutions
import corecodex.lib.helpers as h

log = logging.getLogger(__name__)

# The challenge description class
class ChallengeController(BaseController):
	
	# View a given challenge...
	def challenge_view(self):
		
		# Pull up this challenge's information
		ChallengeID = request.path[request.path.find("challenge/") + 10 : len(request.path)]
		
		# Is this a valid integer?
		if not ChallengeID.isdigit():
			abort(status_code = 404, detail = "Challenge ID \"" + ChallengeID + "\" does not exist.")
		
		# Query the challenge
		Challenge = Challenges.ChallengeQueryID(ChallengeID)
		if Challenge is None:
			abort(status_code = 404, detail = "Challenge ID \"" + ChallengeID + "\" failed to load.")
		if not Challenge.IsValid:
			abort(status_code = 500, detail = "Challenge ID \"" + ChallengeID + "\" failed to load: " + Challenge.ErrorStr)
		
		# Find all user solutions to this Challenge...
		Challenge.solutions = Solutions.SolutionsUserIDChallengeID(session.get("UserID"), ChallengeID)
		Challenge.attempts = len(Challenge.solutions)
		Challenge.solved = False
		
		# Check if we have solved this challenge
		for solution in Challenge.solutions:
			if solution.ResultCode == 1:
				Challenge.solved = True
				break
		
		# Generate graphics / tables
		self.__generate_graphics(ChallengeID)
		
		# Post the owner group of this challenge
		c.groupname = Challenges.ChallengesGroupQueryGroupID(Challenge.ChallengeGroupID, False).ChallengeGroupName
		
		# Convert the source code into html friendly code
		# NOTE: We are defaulting everything to just render in Python
		c.formated_code = h.code_to_html(Challenge.StarterCode, "Python")
		c.formated_samplecode = h.code_to_html(Challenge.SampleCode, "Python")
		
		# Post the challenge view content
		c.challenge = Challenge
		
		# Post the parent group directory
		c.group_id = Challenge.ChallengeGroupID
		c.group_name = c.groupname
		
		# Post the user-level directory data
		c.challenge_id = Challenge.ChallengeID
		c.challenge_name = Challenge.Title
		
		# Render regular form
		c.body_content = render("/content_challengeview.html")
		return render("/theme.html")


	# Generate the google chart graphics and tables
	def __generate_graphics(self, ChallengeID):
		
		# Query all solutions for this challenge
		AllSolutions = Solutions.GetSolutionsChallengeID(ChallengeID)
		SolutionStat = {}
		SolutionLanguage = {}
		SolutionsTotal = 0
		SolutionTimes = {} # Resolution based on 0.5s from 0 to 3 seconds
		
		# Reset internal data structures
		for i in range(9):
			SolutionStat[i] = 0
		for i in range(2 * 3):
			SolutionTimes[i] = 0
		
		# Get all solutions...
		for solution in AllSolutions:
		
			# Count non-failures
			if solution.ResultCode != 0:
				SolutionStat[solution.ResultCode] += 1
				SolutionsTotal += 1
				
				# Count languages (again: must not be a failure)
				if not solution.SourceLanguage in SolutionLanguage:
					SolutionLanguage[solution.SourceLanguage] = 1
				else:
					SolutionLanguage[solution.SourceLanguage] += 1
				
				# Get the current time and cast down to seconds
				# Only save accepted solutions
				if solution.ResultCode == 1:
					RuntimeSeconds = int(float(solution.RuntimeUsage) / 500.0)
					if RuntimeSeconds <= 5:
						SolutionTimes[RuntimeSeconds] += 1
					else:
						SolutionTimes[5] += 1
		
		# If no solutions, just break out
		if SolutionsTotal <= 0:
			c.graph_error_values = ""
			c.graph_error_labels = ""
			c.graph_language_values = ""
			c.graph_language_labels = ""
			c.graph_runtime_values = ""
			c.graph_runtime_labels = ""
			return
		
		# Average out to percentages...
		for i in range(9):
			SolutionStat[i] = 100.0 * float(SolutionStat[i]) / float(SolutionsTotal)
		for k, v in SolutionLanguage.items():
			SolutionLanguage[k] = 100 * float(v) / float(SolutionsTotal)
		
		# Ditionary of common errors
		ErrorDesc = {
			1: "Accepted",
			2: "Compile Time Error",
			3: "Run Time Error",
			4: "Result Does Not Match",
			5: "Result Does Not Match",
			6: "Formatting Error",
			7: "Timed Out",
			8: "Malicious Code Detected",
		}
		
		# Form the graphics strings
		# First: Common failures
		c.graph_error_values = ""
		c.graph_error_labels = ""
		for i in range(1,9):
			if i in SolutionStat and SolutionStat[i] > 0.0:
				c.graph_error_values += "%.1f," % SolutionStat[i]
				c.graph_error_labels += "%d: %.1f%% - %s|" % (i, SolutionStat[i], ErrorDesc[i])
		
		# Remove the trailing symbols...
		c.graph_error_values = c.graph_error_values.rstrip(",")
		c.graph_error_labels = c.graph_error_labels.rstrip("|")
		
		# Second: languages
		c.graph_language_values = ""
		c.graph_language_labels = ""
		for k, v in SolutionLanguage.items():
			c.graph_language_values += str(v) + ","
			c.graph_language_labels += k + "|"
		
		# Remove the trailing symbols...
		c.graph_language_values = c.graph_language_values.rstrip(",")
		c.graph_language_labels = c.graph_language_labels.rstrip("|")
		
		# Third: runtimes
		c.graph_runtime_values = ""
		c.graph_runtime_labels = ""
		index = 0
		for k, v in SolutionTimes.items():
			index += 1
			c.graph_runtime_values += str(v) + ","
			if index < len(SolutionTimes.items()):
				c.graph_runtime_labels += "<%0.1fs|" % (index * 0.5)
		
		# Remove the trailing symbols...
		c.graph_runtime_values = c.graph_runtime_values.rstrip(",")
		c.graph_runtime_labels += ">2.5s"

