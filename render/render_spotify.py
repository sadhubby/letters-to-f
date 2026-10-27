import io
import requests
from PIL import Image, ImageDraw, ImageFont
from config import SPOTIFY_FONT_PATH

def create_diagonal_gradient(width, height, colors):
    """Generates the diagonal multi-stop gradient image."""
    base = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(base)
    
    num_stops = len(colors) - 1
    
    for y in range(height):
        for x in range(width):
            factor = (x + y) / (width + height)
            
            scaled_factor = factor * num_stops
            idx = int(scaled_factor)
            if idx >= num_stops:
                idx = num_stops - 1
                local_factor = 1.0
            else:
                local_factor = scaled_factor - idx
                
            c1 = colors[idx]
            c2 = colors[idx + 1]
            
            r = int(c1[0] + (c2[0] - c1[0]) * local_factor)
            g = int(c1[1] + (c2[1] - c1[1]) * local_factor)
            b = int(c1[2] + (c2[2] - c1[2]) * local_factor)
            
            base.putpixel((x, y), (r, g, b))
            
    return base

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
    """Renders a Spotify card with clean, proportional Montserrat-Bold typography and correct layers."""
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

    # Clean, proportional font sizes using your Montserrat-Bold file
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
            resp = requests.get(album_art_url)
            album_art = Image.open(io.BytesIO(resp.content)).convert("RGB")
            album_art = album_art.resize((art_size, art_size))
            overlay.paste(album_art, (art_x, art_y))
        except Exception:
            draw.rectangle([art_x, art_y, art_x + art_size, art_y + art_size], fill=(35, 25, 55, 255))
    else:
        draw.rectangle([art_x, art_y, art_x + art_size, art_y + art_size], fill=(35, 25, 55, 255))

    # Track Title & Artist Name cleanly aligned below artwork
    text_y = art_y + art_size + 40
    
    # Draw Title (White) & Artist (Pink) using Montserrat-Bold
    draw.text((art_x, text_y), title, font=font_title, fill=(255, 255, 255, 255))
    draw.text((art_x, text_y + 60), artist, font=font_artist, fill=(244, 114, 182, 255))

    # LAYER 3: Composite overlay (Artwork + Crisp Text) directly on top of the textured background
    card.paste(overlay, (0, 0), overlay)

    # Export to RAM buffer
    bio = io.BytesIO()
    bio.name = 'instagram_spotify_square.jpg'
    card.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    return bio