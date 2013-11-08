#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: lib/Challenges.py
# Info: The function-level implementation of programming challenges.
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
from sqlalchemy import types
from corecodex.model.meta import Session, Base
from webhelpers.html import literal
from pylons import session
from corecodex.model import ChallengeDescriptionsTable, ChallengeGroupsTable
import corecodex.lib.Solutions as Solutions
import ConfigParser, csv, sys

# General challenge description class (simply a structure)
class ChallengeDescription:
	
	# True if failed to load
	# The error string is for internal debugging
	IsValid = False
	ErrorStr = ""
	
	# Challenge and challenge group ID
	ChallengeID = -1
	ChallengeGroupID = -1
	
	# Header information: difficulty and supported languages
	Difficulty = 1
	Points = 0
	
	# Note with supported languages, it is an array of strings that
	# must be written comma-delimited array in the file
	# as follows (Not case sensitive):
	# p, py, python -> Python
	# c, c89, c99 -> GCC C
	# cp, cpp, c++ -> C++
	# j, java -> Java
	Languages = []
	
	# General descriptions
	Title = "Default Title"
	ShortDescription = "Default Short Description"
	LongDescription = "Default Long Description"
	
	# Inputs description
	InputDescription = ""
	OutputDescription = ""
	
	# Sample input descriptions
	SampleCode = ""
	SampleInput = ""
	SampleOutput = ""
	
	# Starter code
	StarterCode = ""
	
	# Test inputs and outputs
	TestCode = ""
	TestInput = ""
	TestOutput = ""


# Internal challenge file buffer
# This is a dictionary of all challenge files that are already parsed, so keep them in
# memory rather than re-parse them (Note to self: I should associate a time-out
# variable with this buffer so that over time the files do an implicit refresh)
__ChallengeBufferCache = {}


# Query the given challenge by ID
# Returns None type if not found
def ChallengeQueryID(ChallengeID):
	
	# DEBUGGING CODE: FORCE A CLEAR-CACHE OF THE CHALLENGE BUFFER
	__ChallengeBufferCache = {}
	
	# Is this challenge in our cache?
	if int(ChallengeID) in __ChallengeBufferCache:
		return __ChallengeBufferCache[int(ChallengeID)]
	
	# Else, load from database and place back into the cache
	else:
		
		# Does this challenge exist in the db?
		ExistingChallenges = Session.query(ChallengeDescriptionsTable).filter(ChallengeDescriptionsTable.ChallengeID == ChallengeID).all()
		if len(ExistingChallenges) <= 0:
			return None
		
		# Open and prase the file (or at least attempt)
		Challenge = __ParseChallengeFile(ExistingChallenges[0].ChallengeFileLocation)
		
		# Set target challenge ID and save to the cache
		Challenge.ChallengeID = ChallengeID
		Challenge.ChallengeGroupID = ExistingChallenges[0].ChallengeGroupID
		
		__ChallengeBufferCache[int(ChallengeID)] = Challenge
		
		# Return loaded challenge
		return Challenge


# Open the given challenge file location and parse it
# Returns a challenge description, otherwise posts a failure in the "ErrorString"
def __ParseChallengeFile(ChallengeFileLocation):
	
	# Create a new challenge instance to fill out
	Challenge = ChallengeDescription()
	
	# Parse the challenge configuration file
	try:
		# Open file via configuration parser
		ChallengeFile = ConfigParser.RawConfigParser()
		ChallengeFile.read("corecodex/" + ChallengeFileLocation)
	
	# Catch any errors...
	except:# ConfigParser.Error as error:
		Challenge.ErrorStr = "Parsing failure when reading challenge file \"" + ChallengeFileLocation + "\": "# + error.message
		return Challenge
	
	### Get challenge info from file ###
	
	# Default to no error
	Challenge.ErrorStr = ""
	Challenge.IsValid = False
	
	# Challenge
	Challenge.Title = ChallengeFile.get("challenge", "title")
	if Challenge.Title == None: Challenge.ErrorStr = "Could not find \"description: title\" body"
	
	Challenge.Difficulty = ChallengeFile.getint("challenge", "difficulty")
	if Challenge.Difficulty == None: Challenge.ErrorStr = "Could not find \"challenge: difficulty\" body"
	if Challenge.Difficulty < 0 or Challenge.Difficulty > 5: Challenge.ErrorStr = "Difficulty was out of range of [0, 5]"
	
	Challenge.Languages = __ParseLanguageString(ChallengeFile.get("challenge", "language"))
	if Challenge.Languages == None: Challenge.ErrorStr = "Could not find \"challenge: language\" body"
	if len(Challenge.Languages) <= 0: Challenge.ErrorStr = "Unknown language in supported languages"
	
	Challenge.Points = ChallengeFile.get("challenge", "points")
	if Challenge.Points == None:
		Challenge.ErrorStr = "Could not find \"challenge: points\" body"
	else:
		Challenge.Points = int(Challenge.Points)
	if Challenge.Points < 0: Challenge.ErrorStr = "Challenge has negative points"
	
	# Description
	Challenge.ShortDescription = ChallengeFile.get("description", "shortdesc")
	if Challenge.ShortDescription == None: Challenge.ErrorStr = "Could not find \"description: shortdesc\" body"
	
	Challenge.LongDescription = literal(ChallengeFile.get("description", "longdesc"))
	if Challenge.LongDescription == None: Challenge.ErrorStr = "Could not find \"description: longdesc\" body"
	
	Challenge.InputDescription = literal(ChallengeFile.get("description", "input"))
	if Challenge.InputDescription == None: Challenge.InputDescription = ""
	
	Challenge.OutputDescription = literal(ChallengeFile.get("description", "output"))
	if Challenge.OutputDescription == None: Challenge.OutputDescription = ""
	
	# Starter code
	Challenge.StarterCode = __ParseWhitespaceException(ChallengeFile.get("code", "starter"))
	if Challenge.StarterCode == None: Challenge.ErrorStr = "No starting code available..."
	
	# Sample I/O
	Challenge.SampleCode = __ParseWhitespaceException(ChallengeFile.get("sample", "code"))
	if Challenge.SampleCode == None: Challenge.SampleCode = ""
	
	Challenge.SampleInput = __ParseWhitespaceException(ChallengeFile.get("sample", "input"))
	if Challenge.SampleInput == None: Challenge.SampleInput = ""
	
	Challenge.SampleOutput = __ParseWhitespaceException(ChallengeFile.get("sample", "output"))
	if Challenge.SampleOutput == None: Challenge.SampleOutput = ""
	
	# Testing I/O
	Challenge.TestCode = __ParseWhitespaceException(ChallengeFile.get("test", "code"))
	if Challenge.TestCode == None: Challenge.TestCode = ""
	
	Challenge.TestInput = __ParseWhitespaceException(ChallengeFile.get("test", "input"))
	if Challenge.TestInput == None: Challenge.TestInput = ""
	
	Challenge.TestOutput = __ParseWhitespaceException(ChallengeFile.get("test", "output"))
	if Challenge.TestOutput == None: Challenge.ErrorStr = "Could not find \"test: output\" body"
	
	# Parsing complete - no errors, so flag it as valid
	if len(Challenge.ErrorStr) <= 0:
		Challenge.IsValid = True
	
	# Return data...
	return Challenge


# Parse the given and replace all instances of pipes that are
# the first character, unless it starts with a \|, in which we replace with a pipe
def __ParseWhitespaceException(Code):
	
	# If no code, ignore
	if Code == None:
		return None
	
	# Ignore any input that is 2 char or less (can't clean)
	if len(Code) <= 2:
		return Code
	
	# The result string
	CleanCode = ""
	
	# Ignore the given number of characters
	IgnoreNext = 0
	
	# Replace single-pipes with nothing, and double-pipes with single-pipes,
	# but only at new-lines
	for i in range(0, len(Code)-2):
		
		# Do we have anything to ignore?
		if IgnoreNext > 0:
			IgnoreNext -= 1
		elif (Code[i] == "\n" or i == 0) and Code[i+1] == "|" and Code[i+2] == "|":
			CleanCode += "\n|"
			IgnoreNext = 2
		elif (Code[i] == "\n" or i == 0) and Code[i+1] == "|":
			CleanCode += "\n"
			IgnoreNext = 1
		else:
			CleanCode += Code[i]
	
	# Add back the last two characters
	CleanCode += Code[len(Code)-2]
	CleanCode += Code[len(Code)-1]
	
	# Done cleaning code!
	return CleanCode

# Helper function for parsing the languages string
# See the note in the class structure explaining how the mapping is done
# If there is an unknown language, it is replaced by the empty string
def __ParseLanguageString(Languages):
	
	# If no string, return none
	if Languages == None:
		return None
	
	# Start an empty language list
	LanguageList = []
	CSVParser = csv.reader([Languages], skipinitialspace=True)
	
	# For each element in this list, attempt to map to the appropriate string
	for Result in CSVParser:
		
		# This is just weird... blame it on the CSV convention
		for Language in Result:
			
			# Pull out the language (note the explicit string cast is required)
			Language = Language.lower()
			if Language == "p" or Language == "py" or Language == "python":
				LanguageList.append("Python")
			elif Language == "c" or Language == "c89" or Language == "c99":
				LanguageList.append("GCC C")
			elif Language == "cp" or Language == "cpp" or Language == "c++":
				LanguageList.append("C++")
			elif Language == "j" or Language == "java":
				LanguageList.append("Java")
			else:
				return [] # Return empty list
	
	# Done, return list
	return LanguageList


# Return a list of all challenge groups that this user (identified via the
# session cookie) may attempt to solve. The returned list is a dictionary list
# where you have ID, name, and description
def ChallengesQuery():
	
	# Start the challenges list
	ChallengeGroups = Session.query(ChallengeGroupsTable).all()
	
	# Start challenge list
	ChallengesList = []
	for ChallengeGroup in ChallengeGroups:
		
		# Add to challenge list
		ChallengesList.append(ChallengesGroupQueryGroupID(ChallengeGroup.ChallengeGroupID))
	
	# Done creating the list, return
	return ChallengesList


# Return the meta data associated with the given Challenge group ID
# Note that the default true param "QueryStats" will append group meta data such as averages, completions, etc..
def ChallengesGroupQueryGroupID(ChallengeGroupID, QueryStats = True):
	
	# Query all challenges group
	ChallengeGroups = Session.query(ChallengeGroupsTable).filter(ChallengeGroupsTable.ChallengeGroupID == ChallengeGroupID).all()
	if len(ChallengeGroups) <= 0:
		return None
	
	# Find the challenge
	ChallengeGroup = ChallengeGroups[0]
	
	# Only compute meta if required
	if QueryStats:
		
		# Add some new members that are associated with this user's specific data
		ChallengeGroup.TotalPoints = 0
		ChallengeGroup.AverageDifficulty = 0
		ChallengeGroup.CompletedChallenges = 0
		ChallengeGroup.ChallengeCount = 0
		
		# For each challenge in this group...
		ChallengesGroup = ChallengesQueryGroupID(ChallengeGroupID)
		for ChallengeID in ChallengesGroup:
			
			# Load challenge meta data
			Challenge = ChallengeQueryID(ChallengeID)
			if Challenge:
				ChallengeGroup.TotalPoints += int(Challenge.Points)
				ChallengeGroup.AverageDifficulty += int(Challenge.Difficulty)
				
				# Check completion (is there at least one accepted solution?)
				# Note that we should only count the unique number of solutions
				# So ignore any solutions that share the same id on a sucessfull solution
				if Solutions.HasUserSolvedChallenge(session.get("UserID"), ChallengeID):
					ChallengeGroup.CompletedChallenges += 1
				
		
		# Save the number of challenges
		ChallengeGroup.ChallengeCount = len(ChallengesGroup)
		if ChallengeGroup.ChallengeCount != 0:
			ChallengeGroup.AverageDifficulty /= ChallengeGroup.ChallengeCount
	
	# Return challenge group meta data
	return ChallengeGroup


# Return a list of all challenge from a given group ID
# Returns an array of Challenge IDs based on the given group ID
# as matched within the ChallengeDescriptions list
def ChallengesQueryGroupID(ChallengeGroupID):
	
	# Query all challenges, via filter, of the challenge descriptions
	Challenges = Session.query(ChallengeDescriptionsTable).filter(ChallengeDescriptionsTable.ChallengeGroupID == ChallengeGroupID).all()
	
	# Start challenge list
	ChallengeIDList = []
	for Challenge in Challenges:
		ChallengeIDList.append(Challenge.ChallengeID)
	return ChallengeIDList


# Return a list of all challenge, regardless of group
# Only returns the table data
def QueryAllChallenges():
	
	# Return all challenge IDs
	return Session.query(ChallengeDescriptionsTable).all()

