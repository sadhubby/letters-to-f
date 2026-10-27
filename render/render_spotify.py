import io
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from config import SPOTIFY_FONT_PATH

def create_diagonal_gradient(width, height, colors):
    """Generates a diagonal multi-stop gradient image instantly using NumPy."""
    num_stops = len(colors) - 1
    
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    
    factor = (xx + yy) / 2.0
    scaled_factor = factor * num_stops
    
    idx = np.clip(np.floor(scaled_factor).astype(int), 0, num_stops - 1)
    local_factor = np.clip(scaled_factor - idx, 0.0, 1.0)
    
    c_array = np.array(colors, dtype=float)
    c1 = c_array[idx]
    c2 = c_array[idx + 1]
    
    local_factor_3d = local_factor[..., np.newaxis]
    rgb = c1 + (c2 - c1) * local_factor_3d
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    
    return Image.fromarray(rgb, "RGB")

def add_paper_texture(image: Image.Image) -> Image.Image:
    """Adds the tactile film-grain noise texture."""
    width, height = image.size
    noise = Image.effect_noise((width, height), 55).convert("L")
    textured = Image.blend(image, noise.convert("RGB"), alpha=0.14)
    return textured

def render_spotify_card(
    title: str, 
    artist: str, 
    album_art_url: str = None
) -> io.BytesIO:
    """Renders a Spotify card with clean typography and fast vectorized layers."""
    width, height = 1080, 1080
    
    palette = [
        (18, 16, 38),     # 0%   - Top-Left: Deep moody dark base
        (35, 25, 55),     # 30%  - Extended dark transition
        (120, 45, 95),    # 65%  - Muted dusty rose / mid-tone bridge
        (236, 72, 153),   # 85%  - Soft blooming hot pink
        (244, 114, 182)   # 100% - Bottom-Right: Gentle pastel pink glow
    ]

    # LAYER 1 & 2: Background Gradient & Noise Texture
    card = create_diagonal_gradient(width, height, palette)
    card = add_paper_texture(card)
    
    # Transparent overlay so Artwork & Text sit strictly above the noise layer
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Clean typography setup
    try:
        font_title = ImageFont.truetype(SPOTIFY_FONT_PATH, size=46)
        font_artist = ImageFont.truetype(SPOTIFY_FONT_PATH, size=30)
    except Exception:
        font_title = ImageFont.load_default()
        font_artist = ImageFont.load_default()

    # Balanced Album Art Square (Centered, 560x560)
    art_size = 560
    art_x = (width - art_size) // 2
    art_y = 120

    if album_art_url:
        try:
            resp = requests.get(album_art_url, timeout=5)
            album_art = Image.open(io.BytesIO(resp.content)).convert("RGB")
            album_art = album_art.resize((art_size, art_size))
            overlay.paste(album_art, (art_x, art_y))
        except Exception:
            draw.rectangle([art_x, art_y, art_x + art_size, art_y + art_size], fill=(35, 25, 55, 255))
    else:
        draw.rectangle([art_x, art_y, art_x + art_size, art_y + art_size], fill=(35, 25, 55, 255))

    # Track Title & Artist Name cleanly aligned below artwork
    text_y = art_y + art_size + 40
    
    draw.text((art_x, text_y), title, font=font_title, fill=(255, 255, 255, 255))
    draw.text((art_x, text_y + 60), artist, font=font_artist, fill=(244, 114, 182, 255))

    # LAYER 3: Composite overlay directly on top of the textured background
    card.paste(overlay, (0, 0), overlay)

    # Export to RAM buffer
    bio = io.BytesIO()
    bio.name = 'instagram_spotify_square.jpg'
    card.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    return bio