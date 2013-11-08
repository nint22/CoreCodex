#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: lib/Achievements.py
# Info: The function-level implementation of achivement and user-specific
# achivement data.
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
from sqlalchemy import and_
from corecodex.model.meta import Session, Base
from corecodex.model import AchievementsTable, UserAchievementsTable
from pylons import session

# Start logger
import logging
log = logging.getLogger(__name__)


# Get a list of all achivements
def AchievementsQueryAll():
	
	# Return all achivements
	return Session.query(AchievementsTable).order_by(sa.asc(AchievementsTable.AchievementID)).all()


# Get a list of all achivements this user owns
def AchievementsQueryUserID(UserID):
	
	# Note that we have to do a join between these two tables
	# The user's achivements are listed in UserAchivementsTable but their
	# descriptions are in AchivementsTable
	# SELECT *  
	# FROM   Achievements, UserAchievements 
	# WHERE  Achievements.AchievementID = UserAchievements.AchievementID and UserAchievements.UserID = 4
	JoinedTable = Session.query(AchievementsTable, UserAchievementsTable).filter(and_(AchievementsTable.AchievementID == UserAchievementsTable.AchievementID, UserAchievementsTable.UserID == UserID)).all()
	
	# Generate achievements table
	Achievements = []
	for Item in JoinedTable:
		Achievements.append(Item[0])
	return Achievements

