from flask import Flask, request, url_for, session, redirect, render_template

import base64
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from requests import post,get
import json
import os

CLIENT_ID = "a6b946c08bcb4b18a0a595c22d3bd90d"
CLIENT_SECRET = "8ae15257972544c3831dcabaa7efda37"
TOKEN_INFO = "token_info"
SHORT_TERM = "short_term"
MEDIUM_TERM = "medium_term"
LONG_TERM = "long_term"


def get_temp_token():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_byte = auth_string.encode("utf-8")#encoding the string into a 'utf-8' format
    auth_base64 = str(base64.b64encode(auth_byte), "utf-8")#converting a base 64 object into string

    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"

    }
    data = {"grant_type":"client_credentials"}

    result = post(url, headers=headers, data=data)#results a json string which will be converted to a 
    #python dictionary to access the data

    #loads() means load from string
    json_result = json.loads(result.content)

    token = json_result["access_token"]
    return token



# def get_auth_head(token):
#     return {"Authorization": "Bearer " + token}

# def search_artists(token,name):
#     url = "https://api.spotify.com/v1/search"
#     headers = get_auth_head(token)
#     query = f"?q={name}&type=artist&limit=1"
#     #get artist with the given argument name and only give the top result, hency the limit of 1

#     query_url = url + query
#     result = get(query_url, headers=headers)

#     json_result = json.loads(result.content)['artists']['items']

#     if len(json_result) == 0:
#         print("who is blud even looking for lmao")
#         return None

#     return (json_result[0])


    # print(json_result)

# def get_artist_song(token, artists_id):
#     url = f"https://api.spotify.com/v1/artists/{artists_id}/top-tracks?country=US"
#     #gets the top tracks of the given artist in USA

#     headers = get_auth_head(token)

#     result = get(url, headers=headers)

#     json_result = json.loads(result.content)['tracks']

#     return(json_result)



# token = get_temp_token()
# -----------------------------------------------
# result = (search_artists(token, "The Weeknd"))

# artist_id = result["id"]
# #artist id needed to access the artist's stuff like music and whatnot

# songs = get_artist_song(token, artist_id)

# for index,song in enumerate(songs):
#     print(f"{index + 1}. {song['name']}")

#-------------------------------------------------




app = Flask(__name__)
app.secret_key = os.urandom(24)  

@app.route("/")
def hello_world():
    return render_template('index.html', title = 'welcome to receiptify')

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

    code = request.args.get('code')

    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info

    #print("Token_info stored", session[TOKEN_INFO])

    return redirect(url_for("receipt", _external = True))#redirect yourself to receipt page


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    #print("THIS IS TOKEN_INFO",token_info)
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
