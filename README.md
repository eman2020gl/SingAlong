# SingAlong
Created for AWS hackathon by MachineHack
#SingAlong: A singing companion using AWS serverless architecture

##How it Works

SingAlong API endpoint is setup using AWS API Gateway. The POST method is setup to accept an audio/mp3 ‘content-type’ and triggers a lambda function to store the incoming content into S3 (voice) samples folder  and make an entry in the in-bound queue(SQS) with the S3 link
In-bound queue triggers a lambda function  which uses the S3 link and submits a transcription Job. Once the transcription is complete the transcript text is used to query the DB to find the fuzzy match comparing the transcript text with pre-loaded lyrics text. Fuzzy match is required as the transcript text may not match the lyric text word-to-word.
Based on the match, corresponding S3 link for the full audio media is pre-signed and logged on to the out-bound queue(SQS). The queue in turn triggers the lamda required to invoke SNS for sending out the link.
Meanwhile a Firebase (https://console.firebase.google.com/) account is setup to facilitate push notification. Firebase API Key and mobile device keys  are registered in the SNS dashboard.
SNS uses the above setup to notify the user of the matching song link which is alive for a predetermined time limit

##How to use
Following are the list of AWS components that needs to be created:
####SQS
InQ: To accept incoming voice samples
OutQ: To deliver the song URL to the end-user

####Lambda
InputToQ: Gets triggered from API Gateway. Stores the incoming audio sample and makes an entry in the Input Q.
TranscribeAndMatch: Uses AWS Transcribe to find the transcript for the audio and use the transcript to get the audio file
QueryDB: Invoked by 'TranscribeAndMatch' lambda to get the matching song URL based on the transcript text
ComposeMedley: Invoked by 'TranscribeAndMatch' when user preference is to construct a medley of similar songs
push2Client: Publishes the song URL to client app using AWS SNS and Firebase

####API Gateway
SingAlong API: Create a simple resource 'sing-along' under the root and add 'POST' method beneath it. Configure the API to passthrough content for content-type 'audio/mp3'. Trigger InputToQ to process the incoming content.

####S3 Buckets
Set up two buckets. 'samples' for storing the incoming samples and 'store' to preload with set of full audio files. Also a folder 'vocals' under store bucket to store preprocessed songs that has only vocals and trimmed for removing leading silence.

####DynamoDB
SongDB: A simple no-sql table to store the song title, lyrics text, cluster label and corresponding S3 URLs

####SNS
Set up SNS by adding the platform application endpoint using the Server Key from Firebase project(available in Firebase console) and the device token.

Following are the other components:

Android App: With ability to receive Firebase data notifications
Firebase Project: To push notifications to the specified device endpoint.
KMeans Cluster: Pre-process the lyrics text to generate cluster labels and update the table in DynamoDB.





