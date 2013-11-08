#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: challenges.py
# Info: Challenges view controller; used for browsing challenges
# 
#################################################################

# Standard includes
import logging
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from corecodex.lib.base import BaseController, render
import corecodex.lib.Challenges as Challenges
import corecodex.lib.Solutions as Solutions
import corecodex.lib.Users as Users

# Logging
log = logging.getLogger(__name__)

# General challenges view
class ChallengesController(BaseController):
	
	
	# View all challenges available to thus user
	def challenges_view(self):
		
		# Query all of the challenges this user is bound to
		c.challengesview_challengegroup = Challenges.ChallengesQuery()
		
		# Render regular form
		c.body_content = render("/content_challengesview.html")
		return render("/theme.html")
	
	
	# View a given challenge group...
	def challengegroup_view(self):
		
		# Pull up this challenge's information
		ChallengeGroupID = request.path[request.path.find("challenges/") + 11 : len(request.path)]
		
		# Find the challenge description
		ChallengesID = Challenges.ChallengesQueryGroupID(ChallengeGroupID)
		
		# If list is empty, just error out
		if len(ChallengesID) <= 0:
			abort(status_code = 404, detail = "No challenges in this challenge group.")
		
		# Start challenges meta-info list
		# Note that the second array is index the same and contains
		# a tuple representing the (Attempts / All Users) (Solved / All Attempts)
		ChallengesInfo = []
		ChallengePercentage = []
		
		# Query all the challenges associated with this challenge list
		for ChallengeID in ChallengesID:
			
			# PART 1: Get challenge meta data
			# Get the challenge information
			ChallengeInfo = Challenges.ChallengeQueryID(ChallengeID)
			
			# Query associated challenge solutions
			UserSolutions = Solutions.SolutionsUserIDChallengeID(session.get("UserID"), ChallengeID)
			ChallengeInfo.attempts = len(UserSolutions)
			ChallengeInfo.solved = False
			
			# Does the user's solutions contain at least one valid solution?
			for Attempt in UserSolutions:
				if Attempt.ResultCode == 1:
					ChallengeInfo.solved = True
					break
			
			# Put into challenge list
			ChallengesInfo.append(ChallengeInfo)
			
			# PART 2: Get the attempts / all users and solved / attempts percentage
			UserAttempts = Solutions.GetUserAttemptsCount(ChallengeID) # Number of attempts by users
			UserCount = Users.UserGetUserCount()
			
			TotalSuccess = Solutions.GetSolvedCount(ChallengeID, True) # Yes, count duplicate correct solutions
			AttemptCount = Solutions.GetAttemptsCount(ChallengeID)
			
			# Put into the percentage pair
			if UserCount != 0:
				AttemptsPercent = "%.2f" % (100.0 * float(UserAttempts) / float(UserCount))
			else:
				AttemptsPercent = "0.00"
			
			if AttemptCount != 0:
				SolvedPercent = "%.2f" % (100.0 * float(TotalSuccess) / float(AttemptCount))
			else:
				SolvedPercent = "0.00"
			
			# Put into percentage list
			ChallengePercentage.append([AttemptsPercent, SolvedPercent])
		
		# Post the challenges group info into the mako template context
		c.challengesview_challengesgroup = Challenges.ChallengesGroupQueryGroupID(ChallengeGroupID)
		
		# Post the challenges info into the mako template context
		c.challengesview_challengesmeta = ChallengesInfo
		c.chalenge_percentage = ChallengePercentage
		
		# Post top directory info
		c.group_name = c.challengesview_challengesgroup.ChallengeGroupName
		c.group_id = ChallengeGroupID
		
		# Render regular form
		c.body_content = render("/content_challengeslistview.html")
		return render("/theme.html")

