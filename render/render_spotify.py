import io
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from config import FONT_PATH

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
    """Adds a subtle tactile book-page noise texture over the background."""
    width, height = image.size
    noise = Image.effect_noise((width, height), 55).convert("L")
    textured = Image.blend(image, noise.convert("RGB"), alpha=0.14)
    return textured

def render_poem_card(text: str) -> io.BytesIO:
    """Renders text over a lightning-fast vectorized gradient and paper texture."""
    width, height = 1080, 1080  
    
    palette = [
        (18, 16, 38),     # 0%   - Top-Left: Deep moody dark base
        (35, 25, 55),     # 30%  - Extended dark transition
        (120, 45, 95),    # 65%  - Muted dusty rose / mid-tone bridge
        (236, 72, 153),   # 85%  - Soft blooming hot pink
        (244, 114, 182)   # 100% - Bottom-Right: Gentle pastel pink glow
    ]

    # 1. Generate background gradient instantly & add texture
    img = create_diagonal_gradient(width, height, palette)
    img = add_paper_texture(img)
    
    draw = ImageDraw.Draw(img)

    # 2. Text layout & auto-wrapping constraints
    max_width = width - 180  # 90px side margins
    font_size = 58           
    try:
        font = ImageFont.truetype(FONT_PATH, size=font_size)
    except IOError:
        font = ImageFont.load_default()
    
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