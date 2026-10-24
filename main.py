import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest
from config import BOT_TOKEN, PORT, RENDER_EXTERNAL_URL
from handlers import start_command, handle_poem

async def run_bot():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing! Check your environment variables or .env file.")

    # Configure custom request handler to avoid HTTP/2 hangs on Linux
    custom_request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
        http_version="1.1"  # Forces stable HTTP/1.1 connection
    )

    app = ApplicationBuilder().token(BOT_TOKEN).request(custom_request).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_poem))

    if RENDER_EXTERNAL_URL:
        print(f"Starting bot via Webhook on port {PORT}...")
        await app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}"
        )
    else:
        print("Starting bot locally via polling... Press Ctrl+C to stop.")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        stop_signal = asyncio.get_running_loop().create_future()
        try:
            await stop_signal
        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()

def main():
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\nBot stopped gracefully.")

if __name__ == "__main__":
    main()