#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: users.py
# Info: User log-in, log-out, and registration management
# 
#################################################################

# Standard includes
import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from corecodex.lib.base import BaseController, render
import corecodex.lib.Users as Users
import corecodex.lib.helpers as h
from corecodex.lib import Achievements, Solutions, Challenges
import sqlalchemy, sys

# Start logger
log = logging.getLogger(__name__)

# General user-controller wrapper
class UsersController(BaseController):
	
	
	# User logging-in action and user logging-in
	# POST action (i.e. submitting user log-in event)
	def login(self):
		
		# Attempt a log-in
		user_username = request.params.get("username")
		user_password = request.params.get("password")
		c.login_error = Users.UserLogin(user_username, user_password)
		
		# Redirect as needed if we are already logged-in
		if c.login_error == "redirect":
			redirect(url(controller="main", action="index"))
		
		# Clear out error if the form is just empty
		if len(request.params) == 0:
			c.login_error = ""
		
		# Already logged-in, redirect forward to the main screen
		if len(request.params) == 2 and len(c.login_error) == 0:
			redirect(url(controller="main", action="index"))
		
		# Failed; post error
		else:
			c.body_content = render("/form_login.html")
			return render("/theme.html")
	
	
	# User logging-out action
	def logout(self):
		Users.UserLogout()
		redirect(url(controller="main", action="index"))
	
	
	# User registration action
	def register(self):
		
		# Did we attempt to register?
		user_name = request.params.get("username")
		user_email = request.params.get("useremail")
		user_password = request.params.get("userpassword")
		user_passwordconfirm = request.params.get("userconpassword")
		
		# Attempt to register this user
		c.login_error = Users.UserRegister(user_name, user_email, user_password, user_passwordconfirm)
		
		# Redirect as needed if we are already logged-in
		if c.login_error == "redirect":
			redirect(url(controller="main", action="index"))
		
		# Reset the error message if nothing was posted (i.e. the user loaded this form the first time)
		elif len(request.params) == 0:
			c.login_error = ""
			c.body_content = render("/form_register.html")
		
		# Else, some sort of failure, just post back the error string
		elif len(c.login_error) > 0:
			c.body_content = render("/form_register.html")
		
		# Reset the error message if nothing was posted (i.e. post-back failure)
		elif len(request.params) != 4:
			c.login_error = "Post-back failure. Try to register again."
			c.body_content = render("/form_register.html")
		
		# All checks are applied; user is valid, so log-in for them
		else:
			
			# Force explicit log-in and refresh some of the
			Users.UserLogin(user_name, user_password, True)
			self.BaseController_UpdateUserHeader()
			
			# Post username and render the registered form
			c.user_name = user_name
			c.body_content = render("/form_registered.html")
		
		# Render regular form
		return render("/theme.html")
	
	
	# User un-register action
	def unregister(self):
		
		# Confirm we are already logged in and password
		return "User Unregistration"
	
	# Missing password recovery
	def recover(self):
		
		# Forward to main page if already logged in
		if session.get("UserName"):
			redirect(url(controller="main", action="index"))
		
		# Attempt a recovery
		user_username = request.params.get("username")
		c.recover_error = ""
		
		# If we have no arguments; just post the regular form
		if not user_username:
			c.body_content = render("/form_recover.html")
		
		# Else, attempt to find the user
		else:
			
			# Attempt a recover
			c.recover_error = Users.UserReset(user_username)
			
			# If no error, we recovered correctly
			if len(c.recover_error) <= 0:
				c.body_content = render("/form_recovered.html")
			else:
				c.body_content = render("/form_recover.html")
		
		# Render page
		return render("/theme.html")
	
	
	# View a given user information...
	def user_view(self):
		
		# Pull up this user's information
		UserName = request.path[request.path.find("users/") + 6 : len(request.path)]
		
		# Pull up this user's information
		ExistingUser = Users.UserQueryName(UserName)
		
		# Check for existance
		if not ExistingUser:
			abort(status_code = 404, detail = "User \"" + UserName + "\" does not exist.")
		
		# Basic user information
		c.user = ExistingUser
		c.user_points = Users.UpdateUserPoints(ExistingUser.UserID)
		
		# Post the achivements list
		c.achievements = Achievements.AchievementsQueryUserID(ExistingUser.UserID)
		
		# Find all unique solutions for each challenge, attempts, and succesfull attempts
		c.complete_challenges = []
		c.attempt_count = 0
		c.success_count = 0
		
		# Query all challenges and check each one if we have complete it...
		challenges = Challenges.QueryAllChallenges()
		for challenge in challenges:
			
			# Find all of the solutions for this challenge
			solutions = ChallengeSolutions = Solutions.SolutionsUserIDChallengeID(ExistingUser.UserID, challenge.ChallengeID)
			
			# Add to the number of attempts
			c.attempt_count += len(solutions)
			
			# Add the number of valid attempts
			for solution in solutions:
				if solution.ResultCode == 1:
					c.success_count += 1
			
			# Save any and all solutions
			for solution in solutions:
				
				# Is this a valid solution though?
				if solution.ResultCode == 1:
				
					# Query the challenge to pull out the title and group name
					Challenge = Challenges.ChallengeQueryID(challenge.ChallengeID)
					
					# Query the group
					ChallengeGroup = Challenges.ChallengesGroupQueryGroupID(Challenge.ChallengeGroupID, False)
					
					# Post the challenge title and group name
					UserSolution = {"ChallengeID": Challenge.ChallengeID, "GroupID": Challenge.ChallengeGroupID, "GroupName": ChallengeGroup.ChallengeGroupName, "ChallengeTitle": Challenge.Title, "ChallengePoints": Challenge.Points}
					
					# Put into the list and stop looking for solutions in this group
					c.complete_challenges.append(UserSolution)
					break
					
		
		# Post some statistical data / challenge data
		if c.attempt_count != 0:
			c.challenge_ratio = "%.2f%% (%d/%d)" % (float(float(c.success_count) / float(c.attempt_count)) * 100.0, c.success_count, c.attempt_count)
		else:
			c.challenge_ratio = "No challenges have been attempted"
		
		# Out of all the (valid) solutions, find the fastest (lowest) submission speed and lowest memory usage
		if len(c.complete_challenges) <= 0:
			c.fastest_speed = "No accepted solutions"
			c.smallest_memory = "No accepted solutions"
		else:
			c.fastest_speed = sys.maxint
			c.smallest_memory = sys.maxint
		
		# Find all the valid solutions and get the best run-time speeds and memory usage
		all_solutions = Solutions.SolutionsAcceptedUserID(ExistingUser.UserID)
		for solution in all_solutions:
			if solution.RuntimeUsage < c.fastest_speed:
				c.fastest_speed = solution.RuntimeUsage
			if solution.MemoryUsage < c.smallest_memory:
				c.smallest_memory = solution.MemoryUsage
		
		# Format string
		if len(c.complete_challenges) > 0:
			c.fastest_speed = str(c.fastest_speed) + " milliseconds"
			c.smallest_memory = str(c.smallest_memory) + " kB"
		
		# Render regular form
		c.body_content = render("/content_userview.html")
		return render("/theme.html")
	
	
	# View user's preferences
	def preferences(self):
		
		# Forward to main page if not logged in
		UserID = ""
		if not session.get("UserID"):
			redirect(url(controller="main", action="index"))
		else:
			UserID = session.get("UserID")
		
		# Reset post-back error strings
		c.change_error = ""
		c.icon_error = ""
		c.delete_error = ""
		
		# Are we resetting the password?
		if request.params.get("command") == "change":
			
			# Is the form empty, if so render out regular form
			OldPassword = request.params.get("change_oldpassword")
			NewPassword = request.params.get("change_newpassword")
			ConfirmPassword = request.params.get("change_confirmpassword")
			
			# Default error string to nothing...
			c.change_error = Users.SetUserPassword(session.get("UserName"), OldPassword, NewPassword, ConfirmPassword)
		
		# Else if, are we changing the user's icon?
		elif request.params.get("command") == "icon":
			
			# Set the user's icon ID and internally update as needed
			c.icon_error = Users.UserSetIconID(UserID, request.params.get("iconid"))
			self.BaseController_UpdateUserHeader()
		
		# Else if, are we deleting the account?
		elif request.params.get("command") == "delete":
			
			# Get the post-back
			Password = request.params.get("delete_password")
			ConfirmPassword = request.params.get("delete_confirmpassword")
			
			# Attempt to delete the account; if "deleted" string is returned that means success
			c.delete_error = Users.UserDelete(UserID, Password, ConfirmPassword)
			if c.delete_error == "deleted":
				redirect(url(controller="main", action="index"))
		
		# Post the preferences form
		c.body_content = render("/form_preferences.html")
		return render("/theme.html")
	
	
	# View the leaderboard
	# Note: very slow because of the deep-seeking required; maybe
	# we can do some sort of time-based updates (i.e. every hour
	# we compute the top ten and posts into the database)
	def leaderboard(self):
		
		# Get list of total points
		c.top_scores = Users.GetUsersByScores()
		
		# Get list of most complete challenges
		c.top_challenges = Users.GetUsersByChallenges()
		
		# Get list of highest achievements
		c.top_achievements = Users.GetUsersByAchievements()
		
		# Post the preferences form
		c.body_content = render("/content_leaderboard.html")
		return render("/theme.html")

