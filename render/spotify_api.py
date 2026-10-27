import os
import base64
import httpx
from config import BOT_TOKEN  # or load via os.environ

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_spotify_token():
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    response = httpx.post(url, headers=headers, data=data)
    return response.json().get("access_token")

def fetch_track_info(query: str):
    """Searches Spotify for a track and returns title, artist, and album art URL."""
    token = get_spotify_token()
    if not token:
        return None, None, None

    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": 1}

    response = httpx.get(url, headers=headers, params=params)
    data = response.json()

    items = data.get("tracks", {}).get("items", [])
    if not items:
        return None, None, None

    track = items[0]
    title = track["name"]
    artist = ", ".join([artist["name"] for artist in track["artists"]])
    
    # Get the largest album art image (usually index 0 is 640x640)
    images = track["album"]["images"]
    art_url = images[0]["url"] if images else None

    return title, artist, art_url