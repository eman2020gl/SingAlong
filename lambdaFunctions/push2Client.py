import json
import boto3
# Push the song link from OutQ to the client app using the configure platform app endpoint
def lambda_handler(event, context):
    # Create an SNS client
    sns = boto3.client('sns')
    songLink = event['Records'][0]['body']
    platformAppEndpoint = 'arn:aws:sns:us-east-1:824810731195:endpoint/GCM/Sing_Along/6a02c6cd-f4f2-3638-aa11-07090063ba5a'
    # Publish a simple message to the specified SNS topic
    response = sns.publish(
    TargetArn=platformAppEndpoint,    
    Message= songLink
    
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
