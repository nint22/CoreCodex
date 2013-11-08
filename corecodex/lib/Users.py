#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: lib/Users.py
# Info: The function-level implementation of user and user information
# Note that much of this depends on the model/__init__.py constructs
# that setup the SQLAlchemy connections and table references
#
# Also note that for now, most of these functions are c-like functions
# in that they are all global public and start with Users* such
# as UserLogIn(...), etc...
# 
#################################################################

# Standard includes
import sqlalchemy as sa
import corecodex.lib.helpers as h
import corecodex.lib.Achievements as Achievements
import corecodex.lib.Solutions as Solutions
import corecodex.lib.Challenges as Challenges
from sqlalchemy import types
from corecodex.model.meta import Session, Base
from corecodex.model import UsersTable, AchievementsTable, UserAchievementsTable
from pylons import session
import datetime, hashlib, random
import smtplib
from email.mime.text import MIMEText

# Start logger
import logging
log = logging.getLogger(__name__)


# Return a string that is the SHA512 hash of the given string
# Note: no repeated hashing is done, each hash is the first-level step
def __GeneratePasswordHash(ToHash):
	hasher = hashlib.sha512()
	hasher.update(ToHash + ".om_nom_salt")
	return hasher.hexdigest()


# Login as the given user; returns an empty string upon success,
# else an error string explaining the failure.
# Note: returns the specific string "redirect" if the user is already logged-in
def UserLogin(UserName, UserPassword, IgnoreRedirect = False):
	
	# Check for cookies - are we already logged in?
	if not IgnoreRedirect and session.get("UserName"):
		return "redirect"
	
	# Check for missing strings
	if not UserName:
		return "Error: Missing user name."
	
	if not UserPassword:
		return "Error: Missing password."
	
	# Does this username exist in the db?
	ExistingUsers = Session.query(UsersTable).filter(UsersTable.UserName == UserName).all()
	if len(ExistingUsers) <= 0:
		return "Error: User does not exist."
	
	# Pull up this user's information
	ExistingUser = ExistingUsers[0]
	
	# Hash password
	UserPassword = __GeneratePasswordHash(UserPassword)
	
	# Do the passwords match?
	if ExistingUser.UserPassword != UserPassword:
		return "Error: User password mismatch."
	
	# Update the login count by 1 and the login time
	ExistingUser.LogInCount += 1
	ExistingUser.LastLogin = datetime.datetime.now()
	Session.commit()
	
	# Go ahead and start the cookie!
	session["UserID"] = ExistingUser.UserID
	session["UserName"] = ExistingUser.UserName
	session["UserPoints"] = UpdateUserPoints(ExistingUser.UserID)
	session["UserIconID"] = ExistingUser.IconID
	if ExistingUser.IsAdmin == 1:
		session["IsAdmin"] = True
	else:
		session["IsAdmin"] = False
	session.save()
	
	# All done
	return ""


# Set the given user's icon ID (the icon used in the top-form)
def UserSetIconID(UserID, IconID):
	
	# Convert to integer
	if not IconID.isdigit():
		return "Error: IconID is not an integer."
	else:
		IconID = int(IconID)
	
	# Bounds check the icon ID (should only range betwee [0, 18]
	if IconID < 0 or IconID > 19:
		return "Error: IconID is out of range."
	
	# Update this user's score in the database
	ExistingUsers = Session.query(UsersTable).filter(UsersTable.UserID == UserID).all()
	
	# Commit changes
	if len(ExistingUsers) == 1:
		ExistingUsers[0].IconID = IconID
		Session.commit()
	else:
		return "Error: No users found."
	
	# Post to session if we have a matching ID (otherwise, just return the user points)
	if session.get("UserID") and session["UserID"] == UserID:
		session["UserIconID"] = IconID
		session.save()
	
	# All done!
	return "Icon change saved!"


# Add an achievement to the given user
def UserAddAchievement(UserID, AchievementID):
	
	# Does the current user have this achivement?
	UserAchievements = Achievements.AchievementsQueryUserID(UserID)
	for achievement in UserAchievements:
		if achievement.AchievementID == AchievementID:
			return
	
	# New achievement for this user!
	NewAchievement = UserAchievementsTable()
	NewAchievement.UserID = UserID
	NewAchievement.AchievementID = AchievementID
	
	# Commit to DB
	Session.add(NewAchievement)
	Session.commit()
	
	# Recompute the latest user points and force it onto this user
	UpdateUserPoints(UserID)


# Update the given user's ID and updates the session if the session
# matches the given user ID (so that way we don't mix session data)
def UpdateUserPoints(UserID):
	
	# Start user point count
	UserPoints = 0
	
	# Query all complete unique solutions
	challenges = Challenges.QueryAllChallenges()
	for challenge in challenges:
		if Solutions.HasUserSolvedChallenge(UserID, challenge.ChallengeID):
			UserPoints += Challenges.ChallengeQueryID(challenge.ChallengeID).Points
	
	# Query all achievements
	achievements = Achievements.AchievementsQueryUserID(UserID)
	for achievement in achievements:
		UserPoints += int(achievement.AchievementScore)
	
	# Update this user's score in the database
	ExistingUsers = Session.query(UsersTable).filter(UsersTable.UserID == UserID).all()
	
	# Commit changes
	if len(ExistingUsers) == 1:
		ExistingUsers[0].UserPoints = UserPoints
		Session.commit()
	
	# Post to session if we have a matching ID (otherwise, just return the user points)
	if session.get("UserID") and session["UserID"] == UserID:
		session["UserPoints"] = UserPoints
		session.save()
	return UserPoints


# Logout user (i.e. delete cookie)
def UserLogout():
	session.delete();


# Delete the given user ID
# NOTE: I'm not currently doing a deep deletion
# Returns "deleted" upon success, empty string on non-formed data, and
# and "error: xyz" string upon error 
def UserDelete(UserID, Password, ConfirmPassword):
	
	# Is the form empty? Return no error...
	if not UserID and not Password and not ConfirmPassword:
		return ""
	
	# Do these user passwords match?
	if Password != ConfirmPassword:
		return "Error: Passwords do not match!"
	
	# Get existing user
	ExistingUsers = Session.query(UsersTable).filter(UsersTable.UserID == UserID).all()
	if len(ExistingUsers) <= 0:
		return "Error: User name does not exist."
	ExistingUser = ExistingUsers[0]
	
	# Is the given password the active password?
	ExistingHash = __GeneratePasswordHash(Password)
	if ExistingUser.UserPassword != ExistingHash:
		return "Error: Given password is not correct."
	
	# Delete user from users table
	Session.delete(ExistingUser)
	Session.commit()
	
	# Logout user
	UserLogout()
	
	# Done!
	return "deleted"


# Set the given user's password (if valid)
# Returns an error string that can directly be posted to the user
def SetUserPassword(UserName, ExistingPassword, NewPassword, ConfirmPassword):
	
	# Is the form empty? Return no error...
	if not ExistingPassword and not NewPassword and not ConfirmPassword:
		return ""
	
	# Is the form partially filled?
	elif not ExistingPassword:
		return "Error: Missing existing password."
	elif not NewPassword:
		return "Error: Missing new password."
	elif not ConfirmPassword:
		return "Error: Missing confirmation password."
	
	# Get existing user
	ExistingUsers = Session.query(UsersTable).filter(UsersTable.UserName == UserName).all()
	if len(ExistingUsers) <= 0:
		return "Error: User name does not exist."
	ExistingUser = ExistingUsers[0]
	
	# Is the given password the active password?
	ExistingHash = __GeneratePasswordHash(ExistingPassword)
	if ExistingUser.UserPassword != ExistingHash:
		return "Error: Old password is not correct."
	
	# Check password lengths
	if len(NewPassword) <= 5:
		return "Error: New password is not long enough. Must be at least 6 characters long."
	if len(NewPassword) > 32:
		return "Error: New password is too long. May be at most 32 characters long."
	
	# Validate against whitelist to make sure these are valid characters
	if h.string_check_whitelist(NewPassword, h.string_whitelist_password) == False:
		return "Error: New password contains invalid characters."
	
	# Confirm the passwords are the same...
	if NewPassword != ConfirmPassword:
		return "Error: New passwords do not match."
	
	# All good to go - commit password changes
	ExistingUser.UserPassword = __GeneratePasswordHash(NewPassword)
	Session.commit()
	
	# Done!
	return "Success: Password has changed!"


# Reset password
def UserReset(UserName):
	
	# Get existing user
	ExistingUsers = Session.query(UsersTable).filter(UsersTable.UserName == UserName).all()
	if len(ExistingUsers) <= 0:
		return "Error: User name does not exist."
	
	# Register this new user into the database
	ExistingUser = ExistingUsers[0]
	
	# Randomize an 8-character string
	NewPassword = ""
	for i in range(8):
		NewPassword += random.choice(h.string_whitelist)
	
	# Send an email with the password
	try:
		
		# Form a message
		message = """\
From: do-not-reply@corecodex.com
To: %s
Subject: Password Change

New Password: \"%s\" (Change this as soon as possible!)
Visit www.corecodex.com to learn more.
		""" % (ExistingUser.UserEMail, NewPassword)
		
		# Send mail
		s = smtplib.SMTP()
		s.connect()
		s.sendmail("do-not-reply@corecodex.com", ExistingUser.UserEMail, message)
		s.quit()
		
	except:
		return "Error: Unable to send email. Password was not reset."
	
	# Hash password
	ExistingUser.UserPassword = __GeneratePasswordHash(NewPassword)
	
	# Save changes to DB; done!
	Session.commit()
	return ""


# Register a user; returns an empty string upon success, else an error string
# which can be directly printed back to the user explaining the reason for failure
# Note: returns the specific string "redirect" if the user is already logged-in
def UserRegister(UserName, UserEMail, UserPassword, UserPasswordConfirm):
	
	# Check for cookies - are we already logged in?
	if session.get("UserName"):
		return "redirect"
	
	# Did we get the entire form correctly?
	if not UserName or not UserEMail or not UserPassword or not UserPasswordConfirm:
		return "Error: Missing fields. Please fill out all fields completely."
	
	# Check username lengths
	if len(UserName) <= 5:
		return "Error: User name is not long enough. Must be at least 6 characters long."
	if len(UserName) > 32:
		return "Error: User name is too long. May be at most 32 characters long."
	
	# Check email lengths
	if len(UserEMail) <= 5:
		return "Error: User e-mail is not long enough. Must be at least 6 characters long."
	if len(UserEMail) > 32:
		return "Error: User e-mail is too long. May be at most 32 characters long."
	
	# Check password lengths
	if len(UserPassword) <= 5:
		return "Error: User password is not long enough. Must be at least 6 characters long."
	if len(UserPassword) > 32:
		return "Error: User password is too long. May be at most 32 characters long."
	
	# Validate against whitelist to make sure these are valid characters
	if h.string_check_whitelist(UserName, h.string_whitelist) == False:
		return "Error: User name contains invalid characters."
	if h.string_check_whitelist(UserEMail, h.string_whitelist) == False:
		return "Error: User e-mail contains invalid characters."
	if h.string_check_whitelist(UserPassword, h.string_whitelist_password) == False:
		return "Error: Password contains invalid characters."
	
	# Confirm the passwords are the same...
	if UserPassword != UserPasswordConfirm:
		return "Error: Passwords do not match."
	
	# Finally, make sure no other users with the same name exist..
	ExistingUsers = Session.query(UsersTable).filter(UsersTable.UserName == UserName).all()
	if len(ExistingUsers) > 0:
		return "Error: User name already exists! Please select a new user name."
	
	# Register this new user into the database
	NewUser = UsersTable()
	
	# Note that the user ID will auto-increment
	NewUser.UserName = UserName
	NewUser.UserEMail = UserEMail
	NewUser.UserPoints = 0
	NewUser.UserPassword = __GeneratePasswordHash(UserPassword)
	NewUser.LogInCount = 0
	NewUser.LastLogin = datetime.datetime.now()
	NewUser.IsAdmin = False
	NewUser.IconID = 0
	
	# Commit to DB
	Session.add(NewUser)
	Session.commit()
	
	# Special achivement earned by people who register now - alpha testers
	UserAddAchievement(NewUser.UserID, 0)
	
	# All done
	return ""


# Get a given user's information based on user name (not ID)
def UserQueryName(UserName):
	
	# Does this username exist in the db?
	ExistingUsers = Session.query(UsersTable).filter(UsersTable.UserName == UserName).all()
	if len(ExistingUsers) <= 0:
		return None
	
	# Pull up this user's information
	return ExistingUsers[0]


# Return the number of users as an integer
def UserGetUserCount():
	
	# Return count
	return len(Session.query(UsersTable).all())


# Return the top 10 users based on score
def GetUsersByScores():
	
	# Get existing users based on scores
	ExistingUsers = Session.query(UsersTable).order_by(sa.desc(UsersTable.UserPoints)).all()
	
	# Only return the top 10
	return ExistingUsers[0:10]

# Return the top 10 challenges
def GetUsersByChallenges():
	
	# Get user list
	ExistingUsers = Session.query(UsersTable).all()
	
	# Create challenge count
	UserChallengesComplete = []
	
	# For each user, find out how many challenges they have complete...
	for User in ExistingUsers:
		
		# Total number of challenges complete
		ChallengesComplete = 0
		
		# For each challenge, save solved count
		for Challenge in Challenges.QueryAllChallenges():
			if Solutions.HasUserSolvedChallenge(User.UserID, Challenge.ChallengeID):
				ChallengesComplete += 1
		
		# Push back into the user challenges completion list
		UserChallengesComplete.append([User, ChallengesComplete])
	
	# Sort the user challenges list
	UserChallengesComplete.sort(key=lambda x: x[1])
	UserChallengesComplete.reverse()
	
	# Return the top 10 users
	return UserChallengesComplete[0:10]


# Return the top 10 achievements
def GetUsersByAchievements():
	
	# Get user list
	ExistingUsers = Session.query(UsersTable).all()
	
	# Create achievements count
	UserAchievementsCount = []
	
	# For each user, find out how many achievements they have gotten...
	for User in ExistingUsers:
		
		# Total number of achievements complete
		AchievementsCount = len(Achievements.AchievementsQueryUserID(User.UserID))
		
		# Push back into the user challenges completion list
		UserAchievementsCount.append([User, AchievementsCount])
	
	# Sort the user challenges list
	UserAchievementsCount.sort(key=lambda x: x[1])
	UserAchievementsCount.reverse()
	
	# Return the top 10 users
	return UserAchievementsCount[0:10]

