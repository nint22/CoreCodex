#################################################################
#
# CoreCodex - Online Assessment Tool of Programming Challenges
# Copyright 2011 Core S2 - Software Solutions - See License.txt for info
#
# This source file is developed and maintained by:
# + Jeremy Bridon jbridon@cores2.com
#
# File: lib/Solver.py
# Info: This is the core wrapper of the "exec" method associated
# with verifying if given code is valid. This system should be
# based on a threaded queue so that we don't overwhelm the server
# and security features are all located here.
# 
# Program error codes:
# -1 - Not yet computed
#  0 - Internal failure (Challenge ID doesn't exist, etc..)
#  1 - Accepted
#  2 - Compile time error (see result string)
#  3 - Run time error (see result string)
#  4 - Function results do not match
#  5 - Outputs do not match
#  6 - Formatting failure (when all whitespace is
#      removed, the strings match)
#  7 - Timed out
#  8 - Source not accepted (security)
# 
# Currently supported languages:
#  + Python
#
# Currently supported security:
#  + Removes keywords: "import", "from", "fork", "open", "exec", "execfile", "file", "memoryview", "dir"
#  + Removes comments
#  + Put time out on test process
# 
#################################################################

# Standard includes
import sqlalchemy as sa
import corecodex.lib.helpers as h
import corecodex.lib.Users as Users
import corecodex.lib.Challenges as Challenges
from sqlalchemy import types
from pylons.controllers.util import abort
from corecodex.model.meta import Session, Base
from corecodex.model import ChallengeDescriptionsTable, UserSolutionsTable
import time, datetime, subprocess
import random, sys, os, stat

# Define a solution attempt class
class SolutionAttempt:
	
	# Matches the general setup of user solution
	MemoryUsage = 0
	RuntimeUsage = 0
	ResultCode = 0
	ResultString = ""

# Attempt to execute the given source code against the given solution
# Returns an ID with the solution results; note that solution results are
# not instant because they are 
def SolveChallenge(UserID, ChallengeID, ChallengeSourceCode, ChallengeLanguage):
	
	# Create a new solutions
	Solution = UserSolutionsTable()
	Solution.UserID = UserID
	Solution.ChallengeID = ChallengeID
	Solution.ResultCode = 0
	Solution.ResultString = "Internal CoreJudge Failure."
	Solution.SampleResultString = "" # Leave empty
	Solution.MemoryUsage = 0
	Solution.RuntimeUsage = 0
	Solution.SourceCode = ChallengeSourceCode
	Solution.SourceLanguage = ChallengeLanguage
	Solution.SubmitDateTime = datetime.datetime.now()
	
	# Failure flag
	Failed = False
	
	# Load the challenge information
	Challenge = Challenges.ChallengeQueryID(ChallengeID)
	if not Challenge:
		Failed = True
	
	# Is this a supported language?
	# Formally accepted strings: Python, GCC C, C++, Java
	if not Failed:
		if ChallengeLanguage != "Python" and ChallengeLanguage != "GCC C" and ChallengeLanguage != "C++" and ChallengeLanguage != "Java":
			Failed = True
	
	# Check source code for viability to execute...
	if not Failed:
		SourceSafeErr = __IsSourceSafe(ChallengeSourceCode, ChallengeLanguage)
		if len(SourceSafeErr) > 0:
			Failed = True
			Solution.ResultCode = 8
	
	# Attempt to execute the code against both the challenge test cases and the sample inputs
	if not Failed:
		
		# Execute the sample code
		Attempt = __ExecuteSource(Challenge.SampleCode, Challenge.SampleInput, Challenge.SampleOutput, ChallengeSourceCode, ChallengeLanguage, True)
		Solution.ResultString = Attempt.ResultString
		Solution.SampleResultString = Attempt.ResultString
		
		# Execute the official test case
		# Note that we don't post the result string, we just ignore the output
		# since we do the comparison of correct I/O within the exec source function
		Attempt = __ExecuteSource(Challenge.TestCode, Challenge.TestInput, Challenge.TestOutput, ChallengeSourceCode, ChallengeLanguage)
		Solution.MemoryUsage = Attempt.MemoryUsage
		Solution.RuntimeUsage = Attempt.RuntimeUsage
		Solution.ResultCode = Attempt.ResultCode
		Solution.ResultString = Attempt.ResultString
	
	# Commit to DB
	Session.add(Solution)
	Session.commit()
	
	# Force update the user's score if this solution is valid
	if Solution.ResultCode == 1:
		Users.UpdateUserPoints(UserID)
	
	# Return this new result ID (So the browser redirects)
	return Solution.SolutionID


# Return a result based on the given user ID and result ID
# Returns a "None" upon failure
def QueryResultID(UserID, SolutionID):
	
	# Pull up all solutions with this ID
	Solutions = Session.query(UserSolutionsTable).filter(UserSolutionsTable.SolutionID == SolutionID).all()
	if len(Solutions) <= 0:
		return None
	
	# Check for permissions (we don't want to make all solutions public)
	elif Solutions[0].UserID != UserID:
		return None
	
	# All good, return solution information
	else:
		return Solutions[0]


# Security checks the given source code based on the language
# Only currently supports python
def __IsSourceSafe(SourceCode, SourceLanguage):
	
	# Is this python? If not, fail out
	if SourceLanguage != "Python":
		return "Language not supported by CoreJudge."
	
	# Remove all comments, start with "#" and end with "\n"
	IsComment = False
	CleanSource = ""
	
	# I suppose I could use regex to do this...
	for char in SourceCode:
		if not IsComment and char == "#":
			IsComment = True
		elif IsComment and char == "\n":
			CleanSource += "\n"
			IsComment = False
		elif not IsComment:
			CleanSource += char
	
	# Copy over source code
	SourceCode = CleanSource
	
	# Now create a list of all tokens that are only alpha numeric
	TokenList = []
	TokenBuffer = ""
	for char in SourceCode:
		if char.isalpha() == True:
			TokenBuffer += char
		elif len(TokenBuffer) > 0:
			TokenList.append(TokenBuffer)
			TokenBuffer = ""
	
	# Create a list of illegal keywords
	IllegalKeywords = \
	[
		"import",
		"from",
		"open",
		"exec",
		"execfile",
		"file",
		"memoryview",
		"assert",
		"callable",
		"classmethod",
		"compile",
		"eval",
		"memoryview",
		"staticmethod",
		"builtin",
		"globals",
		"locals",
		"vars",
	]
	
	# For each illegal keyword
	for IllegalKeyword in IllegalKeywords:
		if IllegalKeyword in TokenList:
			return "The illegal keyword \"" + IllegalKeyword + "\" was detected."
	
	# Else, the code is acceptable to execute
	return ""

# Execute the given code against the given challenge
# Internally we are implementing a fork-based (i.e. multi-process)
# solution that creates source files and output files
# Returns a SolutionAttempt instance with error details, etc..
# If SolutionAttempt.ErrorString is longer than 0, then there
# was an error!
# Warning: this isn't at all thread / process safe since its
# possible multiple users could try and delete the same files...
# Note that the last variable "IgnoreResults" ignores the results and simply returns the output
# This is False by default (i.e. we do test the result data)
def __ExecuteSource(ChallengeCode, ChallengeInput, ChallengeOutput, SourceCode, SourceLanguage, IgnoreResults = False):
	
	# Create a new solution attempt
	Attempt = SolutionAttempt()
	Attempt.MemoryUsage = 0
	Attempt.RuntimeUsage = 0
	Attempt.ResultCode = 0
	Attempt.ResultString = ""
	
	# Is this an acceptable source language?
	# Only support Python for now!
	if SourceLanguage != "Python":
		Attempt.ResultCode = 0
		Attempt.ResultString = "Language not supported."
		return Attempt
	
	# Find a valid file name
	FileName = "usercode/Code_%05d.py" % random.randint(0, 99999)
	
	# Create source code with user code
	CodeFile = \
"""
# Includes...
import random

# === START OF USER CODE ===

""" + SourceCode + """

# === END OF USER CODE ===

# Main application entry point
if __name__ == "__main__":
"""
	
	# Challenge test code
	for line in ChallengeCode.split("\n"):
		CodeFile += "\t" + line + "\n"
	
	# Write code to file
	f = open(FileName, "w")
	f.write(CodeFile)
	f.close()
	
	# Open the redirected in, out, and err streams
	fin = open(FileName + "_in", "w")
	fout = open(FileName + "_out", "w")
	ferr = open(FileName + "_err", "w")
	
	# Write out the given input from the challenge description
	fin.write(ChallengeInput)
	
	# Execute the user process
	usr_start = os.times()[2]
	sys_start = os.times()[3]
	UserProcess = subprocess.Popen(["python", FileName], stdin=fin, stdout=fout, stderr=ferr)
	
	# Wait for it to complete...
	for i in range(5):
		if UserProcess.poll() != None:
			break
		else:
			time.sleep(1)
	
	# Kill the process if it is not yet done...
	TimedOut = False
	if UserProcess.poll() == None:
		TimedOut = True
		try:
			UserProcess.kill()
		except OSError:
			pass
	
	# Compute the process times
	usr_end = os.times()[2]
	sys_end = os.times()[3]
	
	# Do we ignore the results?
	if IgnoreResults:
		
		# Only save the output
		fout = open(FileName + "_out", "r")
		Attempt.ResultString = fout.read()
		
		# Release streams
		ferr.close()
		fout.close()
		
	# Else, we do not ignore the results and post-back as much as we can
	else:
		
		# Post back to the attempt (Max 5 seconds)
		# Note we convert it back to milliseconds and cast it down to an integer
		Attempt.RuntimeUsage = int( 1000.0 * ((usr_end - usr_start) + (sys_end - sys_start)) )
		if TimedOut or Attempt.RuntimeUsage >= 5000:
			Attempt.ResultCode = 7
			Attempt.ResultString = "Process timed out: " + str(Attempt.RuntimeUsage) + " ms"
			return Attempt
		
		# Was there an output error?
		ferr = open(FileName + "_err", "r")
		Attempt.ResultString = ferr.read()
		ferr.close()
		
		if len(Attempt.ResultString) > 0:
			Attempt.ResultCode = 3
			return Attempt
		
		# What was the process output?
		fout = open(FileName + "_out", "r")
		Attempt.ResultString = fout.read()
		fout.close()
		
		# If we remove all whitespaces and control characters, and
		# to-lower the characters, are they the same?
		CleanUserOutput = Attempt.ResultString.lower()
		CleanExpectedOutput = ChallengeOutput.lower()
		for c in h.string_whitespaces:
			CleanUserOutput = CleanUserOutput.replace(c, "")
			CleanExpectedOutput = CleanExpectedOutput.replace(c, "")
		
		# Does the user's output match the desired output?
		# Note we ignore the last whitespaces (and control characters) before and after the output blocks
		if Attempt.ResultString.strip(h.string_whitespaces) == ChallengeOutput.strip(h.string_whitespaces):
			Attempt.ResultCode = 1
		
		# If they match, its a formatting failure
		elif CleanUserOutput == CleanExpectedOutput:
			Attempt.ResultCode = 6
		
		# Else, outputs just don't match
		else:
			Attempt.ResultCode = 5
	
	# Return the attempt
	return Attempt

