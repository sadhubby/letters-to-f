from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from render.render_poem import render_poem_card
from render.render_spotify import render_spotify_card

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the user when they open the bot."""
    await update.message.reply_text(
        "✨ Welcome to your Letters for Fiona, a poetry IG Bot!\n\n"
        "Send me any poem or snippet, and I'll generate your square card instantly.\n\n"
        "Don't forget to add a song after your poem using '--'"
    )

async def handle_poem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    if not raw_text.strip():
        return

    # Split poem and song using "--" as the delimiter
    if "--" in raw_text:
        parts = raw_text.split("--", 1)
        poem_text = parts[0].strip()
        song_query = parts[1].strip()
    else:
        poem_text = raw_text.strip()
        song_query = "Die For You - Joji"  # Default fallback if you forget to add a song

    # Parse "Artist - Title" or just use the raw query as the title
    if "-" in song_query:
        # Example: "Joji - Die For You" -> artist="Joji", title="Die For You"
        title_part, artist_part = [p.strip() for p in song_query.split("-", 1)]
        # You can flip these depending on how you prefer to type it (Title - Artist vs Artist - Title)
        artist = title_part 
        title = artist_part
    else:
        artist = "Unknown Artist"
        title = song_query

    await update.message.reply_text(f"🎨 Rendering carousel for your poem & '{title}'...")

    try:
        # Slide 1: Poem Card
        slide1_stream = render_poem_card(poem_text)
        
        # Slide 2: Spotify Track Card (uses whatever you typed after --)
        slide2_stream = render_spotify_card(
            title=title,
            artist=artist,
            album_art_url=None  # Falls back to a clean aesthetic placeholder block if no image URL is provided
        )

        media_group = [
            InputMediaPhoto(media=slide1_stream, caption="Slide 1: Poem"),
            InputMediaPhoto(media=slide2_stream, caption="Slide 2: Associated Track")
        ]

        await context.bot.send_media_group(
            chat_id=update.effective_chat.id,
            media=media_group
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error rendering carousel: {str(e)}")