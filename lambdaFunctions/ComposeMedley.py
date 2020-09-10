from pydub import AudioSegment
from fuzzywuzzy import fuzz
import boto3
from boto3.dynamodb.conditions import Key, Attr
import random
import io
import tempfile
import os
import sys
#import subprocess
import base64
import uuid
sys.path.append('/var/task/ffmpeg')
s3_resource = boto3.resource('s3')
s3Client = boto3.client('s3')

# Find the matching song using transcript Text. Once the matching song is found,
#filter the songs from same cluster and select any random 3 songs to compose medley
def lambda_handler(event,context):

    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('SongDB')
    results = table.scan()
    totalRec = results['ScannedCount']
    #searchString = event['voiceSample']
    searchString = 'Christmas is coming. The Giza getting fat'
    
    maxRatio = 0
    chosenCluster = 0
    # Loop to find the fuzzy match for the transcript text(searchString)
    for i in range(0,totalRec):
        currentRec = results['Items'][i]
        lyricsText = currentRec['Lyrics']
        currentRatio = fuzz.token_set_ratio(searchString, lyricsText)
        if currentRatio > maxRatio:
            maxRatio = currentRatio
            chosenCluster = currentRec['Cluster_Label']
    count = 0
    songList = results['Items']
    similarSongList = filter(lambda song: song['Cluster_Label'] == chosenCluster, songList)
    medleyProbables = list(similarSongList)
    medleySelection= random.sample(range(0,len(medleyProbables)),3) # Select random 3 songs from similar songs list
    AudioSegment.converter = '/var/task/ffmpeg'
    
    bucketName = 'singalong-store-copy'
    
    for x in medleySelection:
        vocalURL = medleyProbables[x]['Vocal_URL']
        bucketKey = 'vocals/' + vocalURL[vocalURL.rfind('/')+1:]
        songLink = s3Client.generate_presigned_url('get_object',
                      Params={'Bucket': bucketName,
                          'Key': bucketKey}, ExpiresIn=180)
        tempString =  '/' + str(x) +'.mp3' 
        tempFileName = tempfile.gettempdir()+ tempString # Use /tmp/ folder provided by Lambda for temporarily storing the downloaded file
        s3Client.download_file(bucketName, bucketKey, tempFileName) 
        #local_filepath = os.path.join(tempfile.gettempdir(), tempFileName)
        
        #Read audio from temp folder
        song = AudioSegment.from_mp3(tempFileName)
        songLength = len(song)
        #print(songLength)
        cutLength = int((songLength/100)*30 ) # Pick first 30% of the song to be part of the medley
        medleyPiece = song[0:cutLength] # Slice the first 30% of the trimmed vocal
        if count == 0:
             medley = medleyPiece
        else:
             medley = medley + medleyPiece
        count = count +1
    #Store the medley on S3 and create a pre-signed URL to be pushed to the client app.
    medleyName = str(uuid4()) + '.mp3'
    content_decoded = base64.b64decode(medley)
    samplesBucketName = 'singalong-samples-copy'
    s3Upload = s3.put_object(Bucket=samplesBucketName,Key=medleyName,Body=content_decoded)
    presigned_song_url = s3Client.generate_presigned_url('get_object',
                      Params={'Bucket': samplesBucketName,
                          'Key': medleyName}, ExpiresIn=180)
    
    return {'statusCode': 200,
            'SongLink': presigned_song_url}
