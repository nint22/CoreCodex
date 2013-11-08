#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: submit.py
# Info: Submission form management; used for managing what is
# being submitted, as well as saves these submissions for user
# statistics
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
import corecodex.lib.Solutions as Solutions


# Logging
log = logging.getLogger(__name__)

# Submission view management
class SubmitController(BaseController):
	
	# Render the submission form
    def submit_view(self):
		
		# Is this a logged-in user? If not, forward them to log-in
		if not session.get("UserName"):
			redirect(url(controller="users", action="login"))
		
		# Get user ID
		UserID = session.get("UserID")
		
		# Pull up this challenge's information
		ChallengeID = request.path[request.path.find("submit/") + 7 : len(request.path)]
		
		# Is this a valid integer?
		if not ChallengeID.isdigit():
			abort(status_code = 404, detail = "Challenge ID \"" + ChallengeID + "\" does not exist.")
		
		# Default form error string
		c.submit_error = ""
		
		# Pull the given post-backs out
		SourceCode = request.params.get("code")
		SourceLanguage = request.params.get("language")
		
		# Query the challenge
		Challenge = Challenges.ChallengeQueryID(ChallengeID)
		if not Challenge:
			abort(status_code = 404, detail = "Challenge ID \"" + ChallengeID + "\" does not exist.")
		
		# Verify file is valid
		if not Challenge.IsValid:
			return Challenge.ErrorStr#abort(status_code = 404, detail = "Challenge ID \"" + ChallengeID + "\" failed to load.")
		
		# Query associated challenge solutions
		UserSolutions = Solutions.SolutionsUserIDChallengeID(session.get("UserID"), ChallengeID)
		Challenge.attempts = len(UserSolutions)
		Challenge.solved = False
		
		# Does the user's solutions contain at least one valid solution?
		for Attempt in UserSolutions:
			if Attempt.ResultCode == 1:
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
		
		# Is this a fresh post-back?
		if not SourceCode or not SourceLanguage:
			
			# Render submission form...
			c.body_content = render("/form_submit.html")
			return render("/theme.html")
		
		# Else, we need to parse the given code!
		else:
			
			# Solve challenge...
			# Note to self: in the future, we will have to have an internal queue system that takes
			# in any number of calls to this function, but only posts back the results when they are ready...
			ResultID = Solver.SolveChallenge(UserID, ChallengeID, SourceCode, SourceLanguage)
			redirect(url(controller="result", action=str(ResultID)))

