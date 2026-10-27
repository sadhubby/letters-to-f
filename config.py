import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
FONT_PATH = "fonts/CrimsonText-Regular.ttf"
SPOTIFY_FONT_PATH = "fonts/Montserrat-Bold.ttf"

PORT = int(os.environ.get("PORT", 8080))
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")