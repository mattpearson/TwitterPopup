# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from win32api import *
from win32gui import *
import win32con
import sys, os
import struct
import time
import pyaudio  
import wave  

# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after
consumer_key=''
consumer_secret=''
    
# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token=''
access_token_secret=''

# Use https://tweeterid.com/ to get the ID for users you want to follow.
#@cnn => 759251
#@wsj => 3108351

follow_list = ['759251','3108351']


# https://stackoverflow.com/questions/17657103/how-to-play-wav-file-in-python
def playChime():
        
    #define stream chunk   
    chunk = 1024  
    
    #open a wav format music  
    f = wave.open(r"chimes.wav","rb")  
    #instantiate PyAudio  
    p = pyaudio.PyAudio()  
    #open stream  
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                    channels = f.getnchannels(),  
                    rate = f.getframerate(),  
                    output = True)  
    #read data  
    data = f.readframes(chunk)  
    
    #play stream  
    while data:  
        stream.write(data)  
        data = f.readframes(chunk)  
    
    #stop stream  
    stream.stop_stream()  
    stream.close()  
    
    #close PyAudio  
    p.terminate()  

# https://stackoverflow.com/questions/33949186/error-when-trying-to-reuse-windows-notification-class-in-python
class WindowsBalloonTip:
    def __init__(self):
        message_map = {
                win32con.WM_DESTROY: self.OnDestroy,
        }
        # Register the Window class.
        wc = WNDCLASS()
        self.hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar"
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        self.classAtom = RegisterClass(wc)

    def ShowWindow(self,title, msg):
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow( self.classAtom, "Taskbar", style, \
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
                0, 0, self.hinst, None)
        UpdateWindow(self.hwnd)
        iconPathName = os.path.abspath(os.path.join( sys.path[0], "balloontip.ico" ))
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
           hicon = LoadImage(self.hinst, iconPathName, \
                    win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
          hicon = LoadIcon(0, win32con.IDI_APPLICATION)
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, \
                         (self.hwnd, 0, NIF_INFO, win32con.WM_USER+20,\
                          hicon, "Balloon  tooltip",msg,200,title))
        playChime()
        time.sleep(3)
        DestroyWindow(self.hwnd)

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0) # Terminate the app.



class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
      try:
        import json
        data = json.loads( data )
        
        user = data['user']
        if( user['id_str'] in follow_list ):
            print('------------')
            print('%s: %s' % ( user['screen_name'], data['text'] )  )
            w.ShowWindow( user['screen_name'], data['text'] )

        return True
      except Exception:
          pass
    def on_error(self, status):

        print(status)

w = WindowsBalloonTip()


if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler( consumer_key, consumer_secret )
    auth.set_access_token( access_token, access_token_secret )

    stream = Stream(auth, l)
    print('Created twitter stream.')
    stream.filter( follow=follow_list) #, track=[''])
    
