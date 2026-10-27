import os
import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN
from handlers import start_command, handle_poem

PORT = int(os.environ.get("PORT", 10000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

async def main():
    # Build the Telegram application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_poem))

    # Initialize core application components
    await app.initialize()
    await app.start()

    if RENDER_EXTERNAL_URL:
        # Production: Start Webhook server for Render
        webhook_url = f"{RENDER_EXTERNAL_URL.rstrip('/')}/{BOT_TOKEN}"
        print(f"Starting bot via Webhook on port {PORT}...")
        
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    else:
        # Local Development: Start Long Polling
        print("Starting bot via Long Polling (Local)...")
        await app.updater.start_polling(drop_pending_updates=True)

    # Keep the event loop running indefinitely until interrupted
    stop_signal = asyncio.Event()
    try:
        await stop_signal.wait()
    finally:
        # Clean shutdown sequence
        await app.stop()
        await app.updater.stop()
        await app.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")