import json
import boto3
import datetime
import awstools
from time import sleep
from math import ceil
from boto3.dynamodb.conditions import Key, Attr
import time

def lambda_handler(event, context):
	problemName = event['problemName']
	submissionId = event['submissionId']
	username = event['username']
	compileError = event['compileError']
	compileErrorMessage = event['compileErrorMessage']
	
	# When there is a compile error, we do not need to update any scores.
	# Just update the compile error message in Dynamo

	if compileError:
		awstools.updateCE(submissionId=submissionId, compileErrorMessage=compileErrorMessage)
		return {'status':200}

	problemInfo = awstools.getProblemInfo(problemName)        

	subtaskDependency = problemInfo['subtaskDependency']
	subtaskMaxScores = problemInfo['subtaskScores']
	testcaseCount = int(problemInfo['testcaseCount'])
	subtaskCount = len(subtaskDependency)
	subtaskScores = [0 for i in range(subtaskCount)]

	submissionInfo = awstools.getSubmission(subId)
	scores = submissionInfo['score'] # List of scores for each testcase

	maxTime = max(submissionInfo['times']) # Maximum runtime across testcases
	maxMemory = max(submissionInfo['memories']) # Maximum memory across testcases
	
	''' BEGIN: EVALUATE CURRENT SUBMISSION '''
	
	def calculateSubtaskScores(subtaskDependency, scores):
		subtaskScores = [100 for i in range(subtaskCount)]
		for i in range(subtaskCount):
			dep = subtaskDependency[i].split(',')
			for t in dep:
				x = t.split('-')
				if(len(x) == 1): # Dependency has single testcase
					ind = int(x[0])
					subtaskScores[i] = min(subtaskScores[i], scores[ind])
				elif len(x) == 2: # Dependency has range of testcases
					st = int(x[0])
					en = int(x[1])
					for j in range(st,en+1):
						subtaskScores[i] = min(subtaskScores[i], scores[j])
		return subtaskScores
	
	subtaskScores = calculateSubtaskScores(subtaskDependency, scores)
	 
	totalScore = 0
	for i in range(subtaskCount):
		totalScore += subtaskScores[i] * subtaskMaxScores[i]

	totalScore /= 100
	totalScore = round(totalScore, 2)

	awstools.updateSubmission(subId, maxTime, maxMemory, subtaskScores, totalScore)

	''' END: EVALUATE CURRENT SUBMISSION ''' 
	submissions = awstools.getStitchSubmissions(username, problemName)
	
	subtaskMaxScores = [0] * subtaskCount
	
	for oldSub in submissions:
		if len(oldSub.scores) != testcaseCount: continue # Invalid submission
		oldSubScores = calculateSubtaskScores(subtaskDependency, oldSub['scores'])
		for subtask in range(subtaskCount):
			subtaskMaxScores[subtask] = max(subtaskMaxScores[subtask], oldSubScores)

	stitchedScore = 0
	for i in range(subtaskCount):
		stitchedScore += subtaskScores[i] * subtaskMaxScores[i]

	userInfo = awstools.getProblemScores(username)
	problemScore = 0
	if problemName in userInfo['problemScores']:
		problemScore = userInfo['problemScores'][problemName]

	if stitchedScore > problemScore:
		awstools.updateUserScore(username, problemName, stitchedScore)
	
	return {
		"statusCode":200
	}
