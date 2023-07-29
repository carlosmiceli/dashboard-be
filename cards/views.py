import os
import dotenv
from urllib.parse import urlencode
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

import random
import requests
import base64
import json
# import logging
# logger = logging.getLogger(__name__)

import gspread
from google.oauth2 import service_account

import openai

dotenv.load_dotenv()

def index(request):
    return render(request, 'home.html')


def usd(request):
    jsonResponse = requests.get(
        'https://api.bluelytics.com.ar/v2/latest').json()
    usdRates = {
        'oficial': jsonResponse['oficial'], 'blue': jsonResponse['blue']}
    return JsonResponse(usdRates)


def quote(request):
    quote_req = requests.get(
        'https://zenquotes.io/api/quotes/').json()
    quote = quote_req[random.randint(0, len(quote_req))]
    return JsonResponse(quote, safe=False)


def history(request):
    month = datetime.now().month
    day = datetime.now().day
    history_req = requests.get(
        f'https://today.zenquotes.io/api/{month}/{day}/').json()
    history_select = history_req['data']['Events'][random.randint(
        0, len(history_req['data']['Events']))]
    return HttpResponse(history_select['html'])

os.environ.get('SPOTIFY_CLIENT_ID'),

def challenges(request):
    try:
        json_data = json.loads(os.environ.get('GOOGLE_SHEETS_JSON'))

        credentials = service_account.Credentials.from_service_account_info(json_data, scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets'])

        client = gspread.authorize(credentials)

        sheet = client.open('Daily Coding Problem').sheet1
        data = sheet.get_all_values()

        def find_array_with_empty_last_element(arrays):
            for array in arrays:
                if array[-1] == "":
                    return array[1]
            return None

        return JsonResponse(find_array_with_empty_last_element(data), safe=False)
    except Exception as e:
        return HttpResponse(e)

def spotify_auth(request):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    redirect_uri = os.environ.get('FE_URL')

    state = "".join(random.choice(chars) for _ in range(16))
    scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private'

    authorize_url = 'https://accounts.spotify.com/authorize?' + urlencode({
        'response_type': 'code',
        'client_id': client_id,
        'scope': scope,
        'redirect_uri': redirect_uri,
        'state': state,
        'show_dialog': True
    })

    return HttpResponse(authorize_url)

def spotify_token(request):
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

    token_url = 'https://accounts.spotify.com/api/token'

    token_data = {
        'grant_type': 'authorization_code',
        'code': request.headers.get('Authorization'),
        'redirect_uri': os.environ.get('FE_URL'),
    }

    credentials = f"{client_id}:{client_secret}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f"Basic {base64_credentials}"
    }

    response = requests.post(token_url, data=token_data, headers=headers)

    if response.status_code == 200:
        access_token = response.json()["access_token"]
        return HttpResponse(access_token)
    else:
        raise Exception('Failed to retrieve Spotify access token')

def spotify_add_songs(request):
    access_token = request.headers.get('Authorization')

    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    check_user = requests.get('https://api.spotify.com/v1/me', headers=headers)

    return JsonResponse({'user': check_user.json(), 'spot': os.environ.get('SPOTIFY_USER_ID')}, safe=False)

    if check_user.json()['id'] != os.environ.get('SPOTIFY_USER_ID'):  
        return HttpResponse('User is not authorized to update this playlist')

    playlists = {
        'progressive_house': {
            'url': 'https://api.spotify.com/v1/playlists/4eaEtTrfBF9VHIgLiNIebR',
            'seed_tracks': [],
        },
        'tech_house': {
            'url': 'https://api.spotify.com/v1/playlists/6j55jcaZ6HG6LRYdz4bhWe',
            'seed_tracks': [],
        },
        'organic_house': {
            'url': 'https://api.spotify.com/v1/playlists/2SeYca0fQkJtOb3qnMcePv',
            'seed_tracks': [],
        },
        'indie_dance': {
            'url': 'https://api.spotify.com/v1/playlists/4PHbRDpJgscmq4b5t6Osok',
            'seed_tracks': [],
        },
        'house': {
            'url': 'https://api.spotify.com/v1/playlists/0HMZkBbQZADPnDqziMdabu',
            'seed_tracks': [],
        }
    }

    recs_url = 'https://api.spotify.com/v1/recommendations'

    # Get each playlist and seed 5 random songs
    for playlist in playlists:
        response = requests.get(playlists[playlist]['url'], headers=headers)

        if response.status_code == 200:
            tracks = random.sample(response.json()['tracks']['items'], 5)
            playlists[playlist]['seed_tracks'].extend([track['track']['id'] for track in tracks])

            
        new_songs_response = requests.get(recs_url, headers=headers, params={'seed_tracks': ",".join(playlists[playlist]['seed_tracks'])})
        
        new_songs = new_songs_response.json()['tracks'][:2]

        spotify_uris = [f"spotify:track:{track['id']}" for track in new_songs]

        
        add_tracks_url = 'https://api.spotify.com/v1/playlists/6BEoKex6bLNP9NPqJAKxTk/tracks'
        requests.post(add_tracks_url, headers=headers, json=spotify_uris)
        
    return HttpResponse('Spotify playlist updated successfully')


def chatbot():
    return True
# openai.api_key  = os.environ.get('OPENAI_API_KEY')
# def get_completion(prompt, model="gpt-3.5-turbo"):
#     messages = [{"role": "user", "content": prompt}]
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=messages,
#         temperature=0, # this is the degree of randomness of the model's output
#     )
#     return response.choices[0].message["content"]