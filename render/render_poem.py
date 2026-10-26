import io
import random
from PIL import Image, ImageDraw, ImageFont
from config import FONT_PATH

def create_diagonal_gradient(width, height, colors):
    """Generates a diagonal multi-stop gradient image."""
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
    """Adds a subtle tactile book-page noise texture over the background."""
    width, height = image.size
    # Increase intensity for that heavy film-grain look (50-60 range)
    noise = Image.effect_noise((width, height), 55).convert("L")
    # Bump alpha to 0.12 - 0.15 for stronger retro grain
    textured = Image.blend(image, noise.convert("RGB"), alpha=0.14)
    return textured

def render_poem_card(text: str) -> io.BytesIO:
    """Renders text over a dynamic square gradient and paper texture."""
    width, height = 1080, 1080  # Changed to 1:1 Square aspect ratio
    
    # Multi-color diagonal palette (Pink -> Purple -> Yellow -> Blue)
    palette = [
        #I like either
        # (26, 22, 45),     # Top-Left: Brief, deep moody dark shadow (near-black/indigo)
        # (157, 23, 77),    # Upper-Mid: Deep, rich rose-magenta
        # (236, 72, 153),   # Lower-Mid: Vibrant hot pink
        # (244, 114, 182)   # Bottom-Right: Soft, glowing pastel pink
        
        (18, 16, 38),     # 0%   - Top-Left: Deep moody dark base
        (35, 25, 55),     # 30%  - Extended dark transition (keeps the top heavy and dark)
        (120, 45, 95),    # 65%  - Muted dusty rose / mid-tone bridge
        (236, 72, 153),   # 85%  - Soft blooming hot pink
        (244, 114, 182)   # 100% - Bottom-Right: Gentle pastel pink glow
    ]

    # 1. Generate background gradient & texture
    img = create_diagonal_gradient(width, height, palette)
    img = add_paper_texture(img)
    
    draw = ImageDraw.Draw(img)

    # 2. Text layout & auto-wrapping constraints (adjusted slightly for square bounds)
    max_width = width - 180  # 90px side margins
    font_size = 58           # Slightly adjusted down for square height constraints
    font = ImageFont.truetype(FONT_PATH, size=font_size)
    
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)

    formatted_text = "\n".join(lines)
    
    # 3. Center text vertically
    total_bbox = draw.multiline_textbbox((0, 0), formatted_text, font=font, spacing=20)
    text_height = total_bbox[3] - total_bbox[1]
    start_y = (height - text_height) // 2

    # 4. Draw crisp white text onto the background
    draw.multiline_text(
        (width // 2, start_y),
        formatted_text,
        fill=(255, 255, 255),
        font=font,
        anchor="ma",
        align="center",
        spacing=20
    )

    # Export to RAM buffer
    bio = io.BytesIO()
    bio.name = 'instagram_poem_square.jpg'
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    return bio