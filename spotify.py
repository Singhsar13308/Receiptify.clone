from flask import Flask, request, url_for, session, redirect, render_template

import base64
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from requests import post,get
import json
import os

CLIENT_ID = "ABC"
CLIENT_SECRET = "XYZ"
TOKEN_INFO = "token_info"
SHORT_TERM = "short_term"
MEDIUM_TERM = "medium_term"
LONG_TERM = "long_term"


app = Flask(__name__)
app.secret_key = os.urandom(24)  

@app.route("/")
def index():
    return render_template('index.html', title = 'Welcome')

@app.route("/login")
def login():
    sp_oauth = SpotifyOAuth(#oauth object for authenticating 
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for("redirectPage", _external = True),#this is the URL to which the user will be redirected after they authenticate with Spotify
        #_external = true ensures an abosulte url in generated
        
        scope = "user-top-read user-library-read"
        #define the permission we requesting from the user: top songs the user listens to and the user's saved tracks and albums

    )
    auth_url = sp_oauth.get_authorize_url()#gets the url which will lead to spotifys authorization page
    return redirect(auth_url)#redirect to authourizing page
    

@app.route("/redirectPage")
def redirectPage():
    
    sp_oauth = SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for("redirectPage", _external = True),
        scope = "user-top-read user-library-read"
    )

    session.clear() 
    # clearing session should get rid of old information and token 

    code = request.args.get('code')

    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info

    #print("Token_info stored", session[TOKEN_INFO])

    return redirect(url_for("receipt", _external = True))#redirect yourself to receipt page

import time
def get_token():
    token_info = session.get(TOKEN_INFO, None)
    
    now = int(time.time())

    expiry_status = token_info['expires_at'] - now < 60
    #if time time to expiry less than 60seconds then we refresh:

    if(expiry_status):
        sp_oauth = SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for("redirectPage", _external = True),
        scope = "user-top-read user-library-read"
    )
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])       


    return token_info

@app.route("/receipt")
def receipt():
    
    user_token = get_token()#get token

    sp = spotipy.Spotify(#make a spotify object
        
        auth = user_token['access_token']

    )

    current_user_name = sp.current_user()['display_name']

    short_term = sp.current_user_top_tracks(
        limit = 10,
        offset = 0,
        time_range = SHORT_TERM
    )
    medium_term = sp.current_user_top_tracks(
        limit = 10,
        offset = 0,
        time_range = MEDIUM_TERM
    )
    long_term = sp.current_user_top_tracks(
        limit = 10,
        offset = 0,
        time_range = LONG_TERM
    )

    if os.path.exists(".cache"): 
        os.remove(".cache")

    return render_template('receipt.html', user_display_name = current_user_name, short_term = short_term, medium_term = medium_term, long_term = long_term)

@app.template_filter('mmss')
def _jinja2_filter_milliseconds(time, fmt=None):
    time = int(time/1000)     # get time into seconds
    minutes = time // 60
    seconds = time % 60

    if seconds < 10:
        return (str(minutes) + ":0" + str(seconds))
    
    return (str(minutes) + ":" + str(seconds))
   


if __name__ == "__main__":
    app.run(host='localhost', port=8080)
