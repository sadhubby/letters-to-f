import os
import asyncio
import tornado.web
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN, PORT, RENDER_EXTERNAL_URL
from handlers import start_command, handle_poem

# Dedicated Health Check Handler for GET requests on root '/'
class HealthCheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(200)
        self.write("Letters to Fiona is healthy and awake!")

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
        # Append /telegram path so POST updates go there, leaving root '/' free for GET pings
        base_url = RENDER_EXTERNAL_URL.rstrip('/')
        webhook_url = f"{base_url}/telegram"
        
        print(f"Setting webhook to: {webhook_url}")
        
        # Automatically register webhook with Telegram on every boot
        await app.bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        
        print(f"Starting bot via Webhook on port {PORT}...")
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="telegram",   # Listens on '/telegram' for Telegram POST requests
            webhook_url=webhook_url,
        )

        # Safely inject the root '/' GET health-check handler into Tornado's app instance
        application_server = getattr(app.updater, "http_server", None)
        if application_server and hasattr(application_server, "app"):
            application_server.app.add_handlers(r".*", [(r"/", HealthCheckHandler)])
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