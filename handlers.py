from telegram import Update
from telegram.ext import ContextTypes
from renderer import render_poem_card

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the user when they open the bot."""
    await update.message.reply_text(
        "✨ Welcome to your Poetry IG Bot!\n\n"
        "Send me any poem or snippet, and I'll generate your square card instantly."
    )

async def handle_poem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catches text messages, generates the square card, and sends it back."""
    poem_text = update.message.text
    
    # Optional safety check if someone sends an empty or weird message
    if not poem_text.strip():
        return

    await update.message.reply_text("🎨 Formatting your square card...")

    try:
        # Calls the renderer function to generate the 1080x1080 image in RAM
        image_stream = render_poem_card(poem_text)
        
        # Send photo back to chat
        await update.message.reply_photo(
            photo=image_stream,
            caption="Here is your formatted card! Tap 'Share to Instagram' to post. 📱✨"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error rendering image: {str(e)}")