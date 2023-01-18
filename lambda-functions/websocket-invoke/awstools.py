import os
import json
import boto3

webSocketURI = os.environ['WebSocketURI']
apigateway = boto3.client('apigatewaymanagementapi', endpoint_url=webSocketURI)
dynamodb = boto3.resource('dynamodb')
judgeName = os.environ['judgeName']
webSocketTable = dynamodb.Table(f'{judgeName}-websocket')

def getAllConnections():
    # For announcement notification
    resp = webSocketTable.scan()['Items']
    connectionIds = [i['connectionId'] for i in resp]
    return connectionIds

def getAllAdmins():
    # For new clarification notification
    return []

def getUser():
    # For clarification response notification
    return []

def invoke(connectionId, body):
    apigateway.post_to_connection(
        ConnectionId = connectionId,
        Data = json.dumps(body)
    )