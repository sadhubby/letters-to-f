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

def register_health_routes(updater):
    httpd = getattr(updater, "_httpd", None)
    http_server = getattr(httpd, "_http_server", None)
    tornado_app = getattr(http_server, "request_callback", None)

    if tornado_app is None:
        print("WARNING: Could not locate the Tornado application; health routes not registered.")
        return False

    tornado_app.add_handlers(r".*$", [
        (r"/", HealthCheckHandler),
        (r"/health", HealthCheckHandler),
    ])
    print("Registered health routes: / and /health")
    return True

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
        
        print(f"Starting bot via Webhook on port {PORT}...")
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="telegram",
            webhook_url=webhook_url,
            drop_pending_updates=True,
        )

        try:
            register_health_routes(app.updater)
        except Exception as e:
            print(f"Could not bind health routes: {e}")

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