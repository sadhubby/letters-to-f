import os
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from handlers import start_command, handle_poem
from telegram.ext import MessageHandler, filters, CommandHandler

PORT = int(os.environ.get("PORT", 10000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

def main():
    # Build the Telegram application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_poem))

    if RENDER_EXTERNAL_URL:
        # Production mode: Run via Webhook on Render
        webhook_url = f"{RENDER_EXTERNAL_URL.rstrip('/')}/{BOT_TOKEN}"
        print(f"Starting bot via Webhook on port {PORT}...")
        
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    else:
        # Local development fallback: Run via Polling
        print("Starting bot via Long Polling (Local)...")
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()