#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: model/__init__.py
# Info: SQLAlchemy / MySQL interface initialization / generalization
# class. The function-level implementations are mostly found within
# the lib/* directiory, such as lib/Users.py for user-related functions
# 
#################################################################

# Standard includes
import sqlalchemy as sa
import corecodex.lib.helpers as h
from sqlalchemy import types
from corecodex.model.meta import Session, Base
from pylons import session
import datetime, hashlib


# Engine initialization global function
def init_model(engine):
	Session.configure(bind=engine)


# Generic user table interface
class UsersTable(Base):
	
	# Define the users table interface
	__tablename__ = "Users"
	
	UserID = sa.Column(types.Integer, primary_key=True)
	UserName = sa.Column(types.Unicode(64))
	UserPoints = sa.Column(types.Integer)
	UserEMail = sa.Column(types.Unicode(64))
	UserPassword = sa.Column(types.Unicode(256))
	LogInCount = sa.Column(types.Integer)
	LastLogin = sa.Column(types.DateTime())
	IsAdmin = sa.Column(types.Boolean)
	IconID = sa.Column(types.Integer)


# Challenge description table
class ChallengeDescriptionsTable(Base):
	
	# Define the users table interface
	__tablename__ = "ChallengeDescriptions"
	__mapper_args__ = dict(order_by="ChallengeID asc")
	
	ChallengeID = sa.Column(types.Integer, primary_key=True)
	ChallengeGroupID = sa.Column(types.Integer)
	ChallengeFileLocation = sa.Column(types.Unicode(1024))


# Challenge groups (grouping of challenge descriptions)
class ChallengeGroupsTable(Base):
	
	# Define the users table interface
	__tablename__ = "ChallengeGroups"
	
	ChallengeGroupID = sa.Column(types.Integer, primary_key=True)
	ChallengeGroupName = sa.Column(types.Unicode(128))
	ChallengeGroupDescription = sa.Column(types.Text)


# User submitted solutions
class UserSolutionsTable(Base):
	
	# Define the users table interface
	__tablename__ = "UserSolutions"
	__mapper_args__ = dict(order_by="SubmitDateTime desc")
	
	SolutionID = sa.Column(types.Integer, primary_key=True)
	UserID = sa.Column(types.Integer)
	ChallengeID = sa.Column(types.Integer)
	ResultCode = sa.Column(types.Integer)
	ResultString = sa.Column(types.Text)
	SampleResultString = sa.Column(types.Text)
	MemoryUsage = sa.Column(types.Integer)
	RuntimeUsage = sa.Column(types.Integer)
	SourceCode = sa.Column(types.Text)
	SourceLanguage = sa.Column(types.Unicode(32))
	SubmitDateTime = sa.Column(types.DateTime())


# Achivement description table
class AchievementsTable(Base):
	
	# Define the achivements description table interface
	__tablename__ = "Achievements"
	
	AchievementID = sa.Column(types.Integer, primary_key=True)
	AchievementIconFileLocation = sa.Column(types.Unicode(1024))
	AchievementName = sa.Column(types.Unicode(128))
	AchievementDescription = sa.Column(types.Unicode(1024))
	AchievementScore = sa.Column(types.Integer)


# Achivement description table
class UserAchievementsTable(Base):
	
	# Define the achivements description table interface
	__tablename__ = "UserAchievements"
	
	UserID = sa.Column(types.Integer, primary_key=True)
	AchievementID = sa.Column(types.Integer)

