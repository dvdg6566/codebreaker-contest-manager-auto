import os
import boto3
import json
from botocore.exceptions import ClientError
from botocore.client import Config
from boto3.dynamodb.conditions import Key, Attr

judgeName = os.environ['judgeName']

dynamodb = boto3.resource('dynamodb','ap-southeast-1')
problems_table = dynamodb.Table(f'{judgeName}-problems')
submissions_table = dynamodb.Table(f'{judgeName}-submissions')
users_table = dynamodb.Table(f'{judgeName}-users')
lambda_client = boto3.client('lambda')

def getProblemScores(username):
    response = users_table.query(
        IndexName = 'usernameIndex',
        ProjectionExpression = 'problemScores'
        KeyConditionExpression=Key('username').eq(username),
    )
    if len(response['Items'] != 1): return None
    return response['Items'][0]

def getProblemInfo(problem):
    response = problems_table.query(
        KeyConditionExpression = Key('problemName').eq(problemName)
    )
    if len(response['Items']) != 1: return None
    return response['Items'][0]

def getSubmission(subId):
    response = submissions_table.query(
        KeyConditionExpression = Key('subId').eq(subId)
    )
    if len(response['Items']) != 1: return None
    return response['Items'][0]

def updateSubmission(subId, maxTime, maxMemory, subtaskScores, totalScore)
    submissions_table.update_item(
        Key={'subId':subId},
        UpdateExpression = f'set maxTime = :maxTime, maxMemory=:maxMemory,subtaskScores=:subtaskScores,totalScore=:totalScore',
        ExpressionAttributeValues={':maxTime':maxTime,':maxMemory':maxMemory,':subtaskScores':subtaskScores,':totalScore':totalScore}
    )

def updateCE(submissionId, compileErrorMessage):
    submissions_table.update_item(
        Key={'subId':submissionId},
        UpdateExpression = f'set compileErrorMessage = :compileErrorMessage',
        ExpressionAttributeValues={':compileErrorMessage':compileErrorMessage}
    )

def getStitchSubmissions(problem, username):
    # Gets list of all submissions made by user to problem
    submissions = submissions_table.query(
        IndexName = 'problemIndex',
        KeyConditionExpression = Key('problemName').eq(problem),
        ProjectionExpression = 'subtaskScores',
        FilterExpression = Attr('username').eq(username),
        ScanIndexForward = False
    )['Items']

    return submissions

def updateUserScore(username, problemName, stitchedScore):
    users_table.update_item(
        Key = {'username' : username},
        UpdateExpression = f'set problemScores. #a =:s',
        ExpressionAttributeValues={':s' : maxScore},
        ExpressionAttributeNames={'#a':problemName}
    )