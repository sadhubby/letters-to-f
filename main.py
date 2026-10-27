import os
import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN
from handlers import start_command, handle_poem

PORT = int(os.environ.get("PORT", 10000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

async def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_poem))

    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL.rstrip('/')}/{BOT_TOKEN}"
        print(f"Starting bot via Webhook on port {PORT}...")
        
        # Manually initialize, set webhook, and start the updater
        await app.initialize()
        await app.bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        await app.start()
        
        # Start the webhook server manually
        from telegram.ext import Defaults
        # Using built-in updater start_webhook with explicit loop control
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=webhook_url,
        )
        
        # Keep the bot running indefinitely
        stop_event = asyncio.Event()
        await stop_event.wait()
    else:
        print("Starting bot via Long Polling (Local)...")
        await app.run_polling(drop_pending_updates=True)

def main():
    # Explicitly create and run the event loop for Python 3.14 compatibility
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("Bot stopped by user.")

if __name__ == "__main__":
    main()