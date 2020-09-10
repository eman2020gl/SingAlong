import json
import boto3
import time
import uuid


transcribe = boto3.client('transcribe')
s3_resource = boto3.resource('s3')
lambdaClient = boto3.client('lambda')
s3Client = boto3.client('s3')

USER_PREFERS_MEDLEY = False # Toggle this to choose between returning single song or a medley of similar songs
#In future implementation, the switch above would be set from the client app

#Use AWS Transcribe to find the transcript for the audio and use the transcript to get the audio file
def lambda_handler(event, context):
    uniqueName = uuid.uuid4() # Unique ID to name the incoming voice sample from user
    samplesBucketName = 's3://singalong-samples-copy/'
    job_name = event['Records'][0]['body'] # Get the audio file from queue (InQ)
    job_uri = samplesBucketName + job_name + '.mp3'

    transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='mp3',
    LanguageCode='en-US',
    OutputBucketName=samplesBucketName
    )
    context.callbackWaitsForEmptyEventLoop = False
    while True: #Wait for the transcription job to complete
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)
        
    #Extract the transcript values once the job is completed
    transcription_job = transcribe.get_transcription_job(TranscriptionJobName=job_name)['TranscriptionJob']
    transcript_file_uri = transcription_job['Transcript']['TranscriptFileUri']
    transcript_path = transcript_file_uri.split("amazonaws.com/", 1)[1]
    transcript_bucket = transcript_path.split('/', 1)[0]
    transcript_key = transcript_path.split('/', 2)[1]
    s3_object = s3_resource.Object(transcript_bucket, transcript_key).get()
    transcript_json = s3_object['Body'].read().decode('utf-8')
    transcript_data = json.loads(transcript_json)
    transcriptResult = transcript_data['results']
    transcriptText = transcriptResult['transcripts'][0]['transcript']

    
    # Getting the link to full media based on transcript text
    inputParam = {
        "voiceSample"   : transcriptText
    }
    if USER_PREFERS_MEDLEY:
        lambdaFunctionName =  'arn:aws:lambda:us-east-1:824810731195:function:ComposeMedley'
    else: # Current Default
        lambdaFunctionName =  'arn:aws:lambda:us-east-1:824810731195:function:QueryDB'
    dbResponse = lambdaClient.invoke(
        FunctionName = lambdaFunctionName,
        InvocationType = 'RequestResponse',
        Payload = json.dumps(inputParam)
    )
    responseContent = json.load(dbResponse['Payload'])
    #print(responseContent)
    songLink = responseContent['SongLink']
    if USER_PREFERS_MEDLEY:
        presigned_song_url = songLink
    else:
        songName = songLink[songLink.rfind('/')+1:] # Extract file name from URL
        # Get the presigned URL for the private media to be shared with the client
        presigned_song_url = s3Client.generate_presigned_url('get_object',
                      Params={'Bucket': 'singalong-store-copy',
                          'Key': songName}, ExpiresIn=120)
                          
    #Queue the response in OutQ to be pushed to the client via SNS
    sqs = boto3.resource('sqs',region_name="us-east-1")
    queue = sqs.get_queue_by_name(QueueName='OutQ')
    queue.send_message(MessageBody=presigned_song_url)
    return {
        'statusCode': 200,
        'songLink': songLink,
        'songName': songName,
        'presignedURL': presigned_song_url
    }
