import json
import awstools

def lambda_handler(event, context):
    
    notificationType = event['notificationType']
    # Notification type is either announce (all users) or clarification (admin only)
    connectionIds = []
    if notificationType == 'announce':
        connectionIds = awstools.getAllConnections()
    elif notificationType == 'newclarification':
        connectionIds = awstools.getAllAdmins()
    elif notificationType == 'answeredclarification':
        body = json.loads(event['body'])
        if 'username' not in body.keys():
            return {
                'statusCode': 400,
                'body': 'Invalid Username!'
            }    
        connectionIds = awstools.getUser(username=body['username'])
    else:
        return {
            'statusCode': 400,
            'body': 'Invalid Status Code!'
        }
    
    print(connectionIds)
    
    body = {'notificationType': notificationType}
    for connectionId in connectionIds:
        awstools.invoke(connectionId = connectionId, body=body)
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
