#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: lib/Solutions.py
# Info: The function-level implementation of solutions for a given user.
# This also includes some statistical analysis and averages function
#
# Also note that for now, most of these functions are c-like functions
# in that they are all global public and start with Users* such
# as UserLogIn(...), etc...
# 
#################################################################

# Standard includes
import sqlalchemy as sa
import corecodex.lib.helpers as h
from sqlalchemy import types
from corecodex.model.meta import Session, Base
from webhelpers.html import literal
from pylons import session
from xml.dom import minidom
from corecodex.model import UserSolutionsTable


# Given a user ID, return all solutions
def SolutionsUserID(UserID):
	
	# Return nothing if we have an invalid user ID or Challenge ID
	if not UserID:
		return []
	
	# Does this challenge exist in the db?
	SolutionsList = Session.query(UserSolutionsTable).filter(UserSolutionsTable.UserID == UserID).all()
	return SolutionsList


# Given a user ID, return all accepted solutions
def SolutionsAcceptedUserID(UserID):
	
	# Return nothing if we have an invalid user ID or Challenge ID
	if not UserID:
		return []
	
	# Does this challenge exist in the db?
	AcceptedSolutionsList = Session.query(UserSolutionsTable).filter(sa.and_(UserSolutionsTable.UserID == UserID, UserSolutionsTable.ResultCode == 1)).all()
	return AcceptedSolutionsList


# Given a challenge ID, return all solutions
def GetSolutionsChallengeID(ChallengeID):
	
	# Return all solutions
	return Session.query(UserSolutionsTable).filter(UserSolutionsTable.ChallengeID == ChallengeID).all()


# Given a user ID and challenge ID, return all solutions for it
def SolutionsUserIDChallengeID(UserID, ChallengeID):
	
	# Return nothing if we have an invalid user ID or Challenge ID
	if not UserID or not ChallengeID:
		return []
	
	# Does this challenge exist in the db?
	SolutionsList = Session.query(UserSolutionsTable).filter(sa.and_(UserSolutionsTable.UserID == UserID, UserSolutionsTable.ChallengeID == ChallengeID)).all()
	return SolutionsList


# Returns true if there is at least one valid solution for the given user ID and challenge ID
def HasUserSolvedChallenge(UserID, ChallengeID):
	
	# Query the list of all attempts by this user for this challenge
	SolutionsList = Session.query(UserSolutionsTable).filter(sa.and_(UserSolutionsTable.UserID == UserID, UserSolutionsTable.ChallengeID == ChallengeID)).all()
	for Solution in SolutionsList:
		if Solution.ResultCode == 1:
			return True
	
	# All done; nothing found
	return False


# Returns true if the user as at least one submission for the given challenge
def HasUserAttemptedChallenge(UserID, ChallengeID):
	
	# Query the list of all attempts by this user for this challenge
	SolutionsList = Session.query(UserSolutionsTable).filter(sa.and_(UserSolutionsTable.UserID == UserID, UserSolutionsTable.ChallengeID == ChallengeID)).all()
	if len(SolutionsList) > 0:
		return True
	else:
		return False


# Returns the number of accepted (i.e. attempts with result codes set to one)
# Note on Allow Duplications param:
# If true, all accepted solutions are counted, otherwise, only the number of solved challenges is counted
def GetSolvedCount(ChallengeID, AllowDuplicates):
	
	# Query the solutions database for only this challenge
	SolutionsList = Session.query(UserSolutionsTable).filter(sa.and_(UserSolutionsTable.ResultCode == 1, UserSolutionsTable.ChallengeID == ChallengeID)).all()
	
	# If we are counting the total number of solutions, including duplicates
	if AllowDuplicates:
		return len(SolutionsList)
	
	# If we are only counting the total solved problems (i.e. no duplicate correct answers...)
	else:
		
		# For each solved solution, place the UserID and ChallengeID into a dictionary
		# If the element already exists, ignore it, it is a re-done solution
		SolutionDict = {}
		for Solution in SolutionsList:
			key = str(Solution.UserID) + "_" + str(Solution.ChallengeID)
			SolutionDict[key] = 1
		
		# Return number of keys
		return len(SolutionDict)
		


# Return the number of valid attempts (i.e. attempts with non-zero result codes)
def GetAttemptsCount(ChallengeID):
	
	# Query the solutions database for only this challenge and only non-zero results
	SolutionsList = Session.query(UserSolutionsTable).filter(sa.and_(UserSolutionsTable.ResultCode != 0, UserSolutionsTable.ChallengeID == ChallengeID)).all()
	
	# Return number solutions
	return len(SolutionsList)


# Return the number of users who have at least attempted the given challenge ID
def GetUserAttemptsCount(ChallengeID):
	
	# Query the solutions database for only this challenge and only non-zero results
	SolutionsList = Session.query(UserSolutionsTable).filter(sa.and_(UserSolutionsTable.ResultCode != 0, UserSolutionsTable.ChallengeID == ChallengeID)).all()

	# Go through the list and count the unique number of users
	UsersList = {}
	for Solution in SolutionsList:
		if not Solution.UserID in UsersList:
			UsersList[Solution.UserID] = 1
	
	# We now have a list of users that have at least attempted the given challenge, now just return the user count
	return len(UsersList)

