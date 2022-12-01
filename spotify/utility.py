import json
from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from requests import post, put, get
from urllib.parse import quote
import environ

env = environ.Env()
environ.Env.read_env()
BASE_URL = "https://api.spotify.com/v1/me/"


def get_user_tokens(guest):
    try:
        user_tokens = SpotifyToken.objects.get(user=guest)
        return user_tokens
    except SpotifyToken.DoesNotExist:
        return None


def update_or_create_user_tokens(
    guest, access_token, token_type, expires_in, refresh_token
):
    tokens = get_user_tokens(guest)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(
            update_fields=["access_token", "refresh_token", "expires_in", "token_type"]
        )
    else:
        tokens = SpotifyToken(
            user=guest,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            expires_in=expires_in,
        )

        tokens.save()


def check_token_if_valid(guest, respond=False):
    tokens = get_user_tokens(guest)
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(guest)
            if respond:
                token = get_user_tokens(guest)
                return token.access_token
        if respond:
            token = get_user_tokens(guest)
            return token.access_token
        return True
    return False


def refresh_spotify_token(guest):
    refresh_token = get_user_tokens(guest).refresh_token
    response = post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": env("CLIENT_ID"),
            "client_secret": env("CLIENT_SECRET"),
        },
    ).json()

    access_token = response.get("access_token")
    token_type = response.get("token_type")
    expires_in = response.get("expires_in")

    update_or_create_user_tokens(
        guest, access_token, token_type, expires_in, refresh_token
    )


def execute_spotify_api_request(guest, endpoint, post_=False, put_=False, url=BASE_URL):
    tokens = get_user_tokens(guest)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + tokens.access_token,
    }
    if post_:
        post(url + endpoint, headers=headers)
    elif put_:
        put(url + endpoint, headers=headers)

    else:
        get(url + endpoint, {}, headers=headers)
    try:
        return "success"
    except:
        return {"error": "Issue with request"}


def play_song(user):
    return execute_spotify_api_request(user, "player/play", put_=True)


def pause_song(user):
    return execute_spotify_api_request(user, "player/pause", put_=True)


def next_song(user):
    return execute_spotify_api_request(user, "player/next", post_=True)


def prev_song(user):
    return execute_spotify_api_request(user, "player/previous", post_=True)


def search_function(query, types, limit, guest):
    formatted_query = quote(query)
    return execute_spotify_api_request(
        guest,
        endpoint=f"?q={formatted_query}&type={types}&limit={limit}",
        url="https://api.spotify.com/v1/search",
    )


def set_track(guest, uri, position=0):
    try:
        tokens = get_user_tokens(guest)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + tokens.access_token,
        }
        data = {
            "uris": [uri],
            "offset": {"position": 0},
            "position_ms": position,
        }

        put(
            BASE_URL + "player/play",
            data=json.dumps(data),
            headers=headers,
        )
        return "success"
    except:
        return {"error": "Issue with request"}


def transfer_play(guest, device_id):
    try:
        tokens = get_user_tokens(guest)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + tokens.access_token,
        }
        data = {"device_ids": [device_id]}

        put(BASE_URL + "player", data=json.dumps(data), headers=headers)
        return "success"
    except:
        return {"error": "Issue with request"}
