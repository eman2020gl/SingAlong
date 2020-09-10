import json
import boto3
import base64
import asyncio
import uuid

#Gets triggered from API Gateway. Stores the incoming audio sample and makes an entry in the Input Q.
def lambda_handler(event,context):
  s3 = boto3.client('s3')
  file_content = event["content"]
  uniqueName = uuid.uuid4()
  bucketName = 'singalong-samples-copy'
  voiceSampleName = str(uniqueName) + ".mp3"
  content_decoded = base64.b64decode(file_content)
  s3_upload = s3.put_object(Bucket=bucketName,Key=voiceSampleName,Body=content_decoded)
  sqs = boto3.resource('sqs',region_name="us-east-1")

  queue = sqs.get_queue_by_name(QueueName='InQ')
  queue.send_message(MessageBody=str(uniqueName))
  return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

