import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY"
PORT = int(os.environ.get("PORT", 10000))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is working!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    if os.environ.get("RENDER"):
        # Webhook mode for Render
        webhook_url = os.environ.get("RENDER_EXTERNAL_URL") + "/" + TOKEN
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=webhook_url
        )
    else:
        # Local polling
        app.run_polling()

if __name__ == "__main__":
    main()
