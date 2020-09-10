from fuzzywuzzy import fuzz
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Query the database for a matching lyrics record which has the highest token match ratio with the transcript text
def lambda_handler(event, context):
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb')
    #Scan the tableto retrieve & loop through the metadata recordset
    table = dynamodb.Table('SongDB')
    results = table.scan()
    totalRec = results['ScannedCount']
    searchString = event['voiceSample']
    returnURL = ''
    lyricsLink = ''
    maxRatio = 0
    for i in range(0,totalRec):
        currentRec = results['Items'][i]
        lyricsText = currentRec['Lyrics']
        currentRatio = fuzz.token_set_ratio(searchString, lyricsText)
        if currentRatio > maxRatio:
            maxRatio = currentRatio
            lyricsLink = currentRec['Storage_URL']
        
    #print(currentRec['Author'])
    #print(currentRatio)
    return {
        'statusCode': 200,
        'SongLink': lyricsLink,
        'MaxRatio': maxRatio
        }
