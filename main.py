import os
import asyncio
import tornado.web
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN, PORT, RENDER_EXTERNAL_URL
from handlers import start_command, handle_poem

# Custom Tornado handler for GET pings (Health Check)
class HealthCheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(200)
        self.write("Letters for Fiona is healthy and awake!")

async def main():
    print(f"--- STARTUP DIAGNOSTICS ---")
    print(f"BOT_TOKEN present: {bool(BOT_TOKEN)}")
    print(f"RENDER_EXTERNAL_URL: {RENDER_EXTERNAL_URL}")
    print(f"PORT: {PORT}")
    print(f"---------------------------")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command and message handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_poem))

    await app.initialize()
    await app.start()

    if RENDER_EXTERNAL_URL:
        # Standardize webhook URL to the root domain '/'
        webhook_url = RENDER_EXTERNAL_URL.rstrip('/')
        print(f"Setting webhook to: {webhook_url}")
        
        # Explicitly register root webhook URL with Telegram
        await app.bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        
        print(f"Starting bot via Webhook on port {PORT}...")
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="",          # Listens on '/' for Telegram POST requests
            webhook_url=webhook_url,
        )

        # Attach custom GET health-check route to Tornado web server
        app.updater.http_server.app.add_handlers(
            r".*",
            [(r"/", HealthCheckHandler)]
        )
    else:
        print("WARNING: RENDER_EXTERNAL_URL is missing! Falling back to Long Polling...")
        await app.updater.start_polling(drop_pending_updates=True)

    stop_signal = asyncio.Event()
    try:
        await stop_signal.wait()
    finally:
        await app.stop()
        await app.updater.stop()
        await app.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")