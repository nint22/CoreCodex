#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: results.py
# Info: Views results to the owner; only the owner may view his or
# her results
#
# Note that actual execution of submission and the whole feature-set
# associated with that is within the "lib/Submit.py" file
# 
#################################################################

# Standard includes
import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from corecodex.lib.base import BaseController, render
import corecodex.lib.Challenges as Challenges
import corecodex.lib.Solver as Solver
import corecodex.lib.helpers as h
import corecodex.lib.Solutions as Solutions
import corecodex.lib.Users as Users

# Logging
log = logging.getLogger(__name__)

# Submission view management
class ResultsController(BaseController):
	
	# Render the submission form
	def result_view(self):
		
		# Is this a logged-in user? If not, forward them to log-in
		UserID = session.get("UserID")
		if not UserID:
			redirect(url(controller="users", action="login"))
		
		# Pull up this results's information
		ResultID = request.path[request.path.find("result/") + 7 : len(request.path)]
		
		# Query the results information
		Solution = Solver.QueryResultID(UserID, ResultID)
		
		# If no solution, post error
		if not Solution:
			abort(status_code = 404, detail = "Result ID \"" + ResultID + "\" does not exist.")
		
		# Query the challenge
		# Note to self: can I directly access via foriegn key?
		Challenge = Challenges.ChallengeQueryID(Solution.ChallengeID)
		if not Challenge:
			abort(status_code = 404, detail = "Challenge ID \"" + Solution.ChallengeID + "\" does not exist.")
		
		# Find all user solutions to this Challenge...
		Challenge.solutions = Solutions.SolutionsUserIDChallengeID(UserID, Solution.ChallengeID)
		Challenge.attempts = len(Challenge.solutions)
		Challenge.solved = False
		
		# Check if we have solved this challenge
		for solution in Challenge.solutions:
			if solution.ResultCode == 1:
				Challenge.solved = True
				break
		
		# Post the owner group of this challenge
		c.groupname = Challenges.ChallengesGroupQueryGroupID(Challenge.ChallengeGroupID, False).ChallengeGroupName
		
		# Post the challenge view content
		c.challenge = Challenge
		
		# Post the parent group directory
		c.group_id = Challenge.ChallengeGroupID
		c.group_name = c.groupname
		
		# Post the user-level directory data
		c.challenge_id = Challenge.ChallengeID
		c.challenge_name = Challenge.Title
		
		# Convert the source code into html friendly code
		# NOTE: We are defaulting everything to just render in Python
		c.formated_code = h.code_to_html(Solution.SourceCode, "Python")
		c.formated_samplecode = h.code_to_html(Challenge.SampleCode, "Python")
		
		# Render the solution information
		c.challenge = Challenge
		c.result = Solution
		c.body_content = render("/content_resultview.html")
		return render("/theme.html")
	
	
	# Render the submission form
	def results_view(self):
		
		# Pull up this user's information
		UserName = request.path[request.path.find("results/") + 8 : len(request.path)]
		
		# Pull up this user's information
		ExistingUser = Users.UserQueryName(UserName)
		
		# Check for existance
		if not ExistingUser:
			abort(status_code = 404, detail = "User name \"" + UserName + "\" does not exist.")
		
		# Solution list
		c.solutions = []
		
		# Build a solutions list with connected data (i.e. challenge name, group name, etc..)
		solutions = Solutions.SolutionsUserID(ExistingUser.UserID)
		for solution in solutions:
		
			# Query the challenge to pull out the title and group name
			Challenge = Challenges.ChallengeQueryID(solution.ChallengeID)
			
			# Query the group
			ChallengeGroup = Challenges.ChallengesGroupQueryGroupID(Challenge.ChallengeGroupID, False)
			
			# Post the challenge title and group name
			UserSolution = {"SolutionID": solution.SolutionID, "ChallengeID": solution.ChallengeID, "GroupName": ChallengeGroup.ChallengeGroupName, "GroupID": ChallengeGroup.ChallengeGroupID, "ChallengeTitle": Challenge.Title, "SubmissionDate": solution.SubmitDateTime, "MemoryUsage": solution.MemoryUsage, "RuntimeUsage": solution.RuntimeUsage, "ResultCode": solution.ResultCode}
			
			# Append to list
			c.solutions.append(UserSolution)
		
		# Render page
		c.body_content = render("/content_resultsview.html")
		return render("/theme.html")

