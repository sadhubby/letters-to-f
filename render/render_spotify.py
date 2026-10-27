import io
import requests
from PIL import Image, ImageDraw, ImageFont
from config import FONT_PATH

def render_spotify_card(
    title: str, 
    artist: str, 
    album_art_url: str = None
) -> io.BytesIO:
    """Renders a 1080x1080 aesthetic Spotify player slide without the timer bar."""
    width, height = 1080, 1080
    
    # Dark moody background matching your poem card's top-left
    card = Image.new("RGB", (width, height), color=(18, 16, 38))
    draw = ImageDraw.Draw(card)

    try:
        font_large = ImageFont.truetype(FONT_PATH, size=52)
        font_medium = ImageFont.truetype(FONT_PATH, size=36)
    except:
        font_large = font_medium = ImageFont.load_default()

    # Larger Album Art Square (Centered, 640x640) since we have extra space without the bar
    art_size = 640
    art_x = (width - art_size) // 2
    art_y = 140

    if album_art_url:
        try:
            resp = requests.get(album_art_url)
            album_art = Image.open(io.BytesIO(resp.content)).convert("RGB")
            album_art = album_art.resize((art_size, art_size))
            card.paste(album_art, (art_x, art_y))
        except Exception:
            draw.rectangle([art_x, art_y, art_x + art_size, art_y + art_size], fill=(35, 25, 55))
    else:
        draw.rectangle([art_x, art_y, art_x + art_size, art_y + art_size], fill=(35, 25, 55))

    # Track Title & Artist Name positioned neatly below the artwork
    text_y = art_y + art_size + 50
    
    # Draw Title
    draw.text((art_x, text_y), title, font=font_large, fill=(255, 255, 255))
    # Draw Artist with your pink accent color
    draw.text((art_x, text_y + 70), artist, font=font_medium, fill=(236, 72, 153))

    bio = io.BytesIO()
    bio.name = 'instagram_spotify_square.jpg'
    card.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    return bio