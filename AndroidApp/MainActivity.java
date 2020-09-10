package com.example.singalong;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.text.Html;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import android.text.method.LinkMovementMethod;

import com.google.firebase.iid.FirebaseInstanceId;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;
public class MainActivity extends AppCompatActivity implements View.OnClickListener{
    private static final String TAG = "MainActivity";
    private Button UploadBtn, SelectBtn;
    private EditText FileNameEdit;
    private final int FILE_REQUEST =1;
    public TextView SongTxt;
    protected SingAlong myApp ;

    public boolean updateMessage(String message) {
        SongTxt = (TextView)findViewById(R.id.txtSongLink) ;
        String songLinkText = "<a href='" + message +"'> Song Link</a>";
        SongTxt.setText(Html.fromHtml(songLinkText));
        SongTxt.setMovementMethod(LinkMovementMethod.getInstance());

        return true;
    }

    public void showMessage(String message) {
        FileNameEdit.setText(message);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        myApp = (SingAlong) this.getApplicationContext() ;
        //Activity currentActivity = ((SingAlong) getApplicationContext()).getCurrentActivity() ;
        Button TokenBtn = (Button)findViewById(R.id.btnToken);
        SongTxt = (TextView)findViewById(R.id.txtSongLink) ;
        //SongTxt.setText("Test Link");
        SongTxt.setClickable(true);
        String text = "<a href='http://www.google.com'> Test Link </a>";
        SongTxt.setMovementMethod(LinkMovementMethod.getInstance());
        SongTxt.setText(Html.fromHtml(text));
        TokenBtn.setOnClickListener(this);
    }
    @Override
    protected void onResume () {
        super.onResume() ;
        myApp.setCurrentActivity( this ) ;
    }
    @Override
    protected void onPause () {
        clearReferences() ;
        super.onPause() ;
    }
    @Override
    protected void onDestroy () {
        clearReferences() ;
        super.onDestroy() ;
    }
    private void clearReferences () {
        Activity currActivity = myApp.getCurrentActivity() ;
        if ( this.equals(currActivity))
            myApp.setCurrentActivity( null ) ;
    }
    @Override
    public void onClick(View view) {
        switch (view.getId()){
            case R.id.btnSelect:
                selectFile();
                break;
            case R.id.btnToken:
                String token = FirebaseInstanceId.getInstance().getToken();
                Log.d(TAG,token);
                Toast.makeText(MainActivity.this,token,Toast.LENGTH_SHORT).show();
        }
    }
    private void selectFile()
    {
        Intent intent = new Intent();
        intent.setType("file/*");
        intent.setAction(Intent.ACTION_GET_CONTENT);
        startActivityForResult(intent,FILE_REQUEST);

    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if(requestCode==FILE_REQUEST && resultCode == RESULT_OK && data!= null)
        {
            Uri path = data.getData();
            //MediaStore.Files.getContentUri()

        }
    }
}
