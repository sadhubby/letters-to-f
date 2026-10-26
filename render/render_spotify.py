import io
import requests
from PIL import Image, ImageDraw, ImageFont
from config import FONT_PATH

def render_spotify_card(
    title: str, 
    artist: str, 
    album_art_url: str = None, 
    duration_str: str = "3:31", 
    current_time_str: str = "1:47"
) -> io.BytesIO:
    """Renders a 1080x1080 aesthetic Spotify player slide matching the dark vibe."""
    width, height = 1080, 1080
    
    # Consistent dark background matching the top-left of your poem card
    card = Image.new("RGB", (width, height), color=(18, 16, 38))
    draw = ImageDraw.Draw(card)

    try:
        font_large = ImageFont.truetype(FONT_PATH, size=52)
        font_medium = ImageFont.truetype(FONT_PATH, size=36)
        font_small = ImageFont.truetype(FONT_PATH, size=24)
    except:
        font_large = font_medium = font_small = ImageFont.load_default()

    # Album Art Square (Centered, 520x520)
    art_size = 520
    art_x = (width - art_size) // 2
    art_y = 160

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

    # Track Title & Artist Name
    text_y = art_y + art_size + 60
    draw.text((art_x, text_y), title, font=font_large, fill=(255, 255, 255))
    draw.text((art_x, text_y + 70), artist, font=font_medium, fill=(236, 72, 153)) # Accent pink for artist

    # Progress Bar
    bar_y = text_y + 175
    bar_width = art_size
    progress_point = int(bar_width * 0.50) # 50% played

    # Track background line
    draw.line([(art_x, bar_y), (art_x + bar_width, bar_y)], fill=(60, 45, 85), width=6)
    # Played progress line (pink accent)
    draw.line([(art_x, bar_y), (art_x + progress_point, bar_y)], fill=(244, 114, 182), width=6)
    # Scrubber head dot
    draw.ellipse([art_x + progress_point - 8, bar_y - 8, art_x + progress_point + 8, bar_y + 8], fill=(255, 255, 255))

    # Time Stamps
    draw.text((art_x, bar_y + 15), current_time_str, font=font_small, fill=(160, 150, 180))
    
    bbox = draw.textbbox((0, 0), duration_str, font=font_small)
    duration_w = bbox[2] - bbox[0]
    draw.text((art_x + bar_width - duration_w, bar_y + 15), duration_str, font=font_small, fill=(160, 150, 180))

    bio = io.BytesIO()
    bio.name = 'instagram_spotify_square.jpg'
    card.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    return bio