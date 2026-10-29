import os
import asyncio
import tornado.web
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN, PORT, RENDER_EXTERNAL_URL
from handlers import start_command, handle_poem

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

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_poem))

    await app.initialize()
    await app.start()

    if RENDER_EXTERNAL_URL:
        base_url = RENDER_EXTERNAL_URL.rstrip('/')
        webhook_url = f"{base_url}/telegram"
        
        print(f"Setting webhook to: {webhook_url}")
        await app.bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        
        print(f"Starting bot via Webhook on port {PORT}...")
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="telegram",
            webhook_url=webhook_url,
        )

        # Correct attribute inspection for python-telegram-bot v21.x Tornado app instance
        try:
            # PTB stores the Tornado application inside updater.http_server.application
            http_server_obj = getattr(app.updater, "_http_server", None) or getattr(app.updater, "http_server", None)
            if http_server_obj and hasattr(http_server_obj, "application"):
                http_server_obj.application.wildcard_router.rules.insert(
                    0, tornado.web.url(r"/", HealthCheckHandler)
                )
                print("Successfully injected root '/' health check route into Tornado router.")
        except Exception as e:
            print(f"Could not bind root route dynamically: {e}")

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