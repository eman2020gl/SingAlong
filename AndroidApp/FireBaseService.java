package com.example.singalong;

import android.app.Activity;
import android.app.ActivityManager;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.widget.TextView;

import androidx.core.app.NotificationCompat;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import java.util.Map;
import java.util.MissingFormatArgumentException;
//A simple Firebase service class to receive in app notification
public class FireBaseService extends FirebaseMessagingService {
            static protected int id = 0;
            Context context;
            public FireBaseService(Context context){
                 this.context=context;
                 }
    public FireBaseService(){
                  }

    @Override
        public void onMessageReceived(RemoteMessage remoteMessage) {
            super.onMessageReceived(remoteMessage);
                //NotificationCompat.Builder mBuilder = new NotificationCompat.Builder(this);
                //mBuilder.setContentTitle(getString(R.string.app_name));
                final Map<String, String> message = remoteMessage.getData();
                final String actualMessage = message.get("default").toString();
                final Activity currentActivity = ((SingAlong)getApplicationContext()).getCurrentActivity();
        currentActivity.runOnUiThread(new Runnable() {

            @Override
            public void run() {
                //Update the main UI thread, since MainActivity is running in main UI thread
                ((MainActivity)currentActivity).updateMessage(actualMessage);
            }
        });

                    }

    }

