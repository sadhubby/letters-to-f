from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from render.render_poem import render_poem_card
from render.render_spotify import render_spotify_card
from render.spotify_api import fetch_track_info

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the user when they open the bot."""
    await update.message.reply_text(
        "✨ Welcome to your Letters for Fiona, a poetry IG Bot!\n\n"
        "Send me any poem for a single card, or add '-- Song Name' at the bottom to generate a 2-slide carousel!"
    )

async def handle_poem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    if not raw_text.strip():
        return

    # Check if user included the "--" delimiter for a song
    if "--" in raw_text:
        parts = raw_text.split("--", 1)
        poem_text = parts[0].strip()
        song_query = parts[1].strip()

        await update.message.reply_text(f"🎨 Rendering 2-slide carousel (Poem + '{song_query}')...")

        try:
            # Slide 1: Poem Card
            slide1_stream = render_poem_card(poem_text)
            
            # Fetch real metadata from Spotify API
            title, artist, album_art_url = fetch_track_info(song_query)
            
            if not title:
                title = song_query
                artist = "Unknown Artist"
                album_art_url = None

            # Slide 2: Spotify Track Card
            slide2_stream = render_spotify_card(
                title=title,
                artist=artist,
                album_art_url=album_art_url
            )

            media_group = [
                InputMediaPhoto(media=slide1_stream, caption="Slide 1: Poem"),
                InputMediaPhoto(media=slide2_stream, caption=f"Slide 2: {title} — {artist}")
            ]

            await context.bot.send_media_group(
                chat_id=update.effective_chat.id,
                media=media_group
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Error rendering carousel: {str(e)}")

    else:
        # SINGLE SLIDE MODE (No "--" provided)
        poem_text = raw_text.strip()
        await update.message.reply_text("🎨 Rendering single poem card...")

        try:
            slide1_stream = render_poem_card(poem_text)
            await update.message.reply_photo(
                photo=slide1_stream,
                caption="Here is your poem card."
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error rendering poem card: {str(e)}")