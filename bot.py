import os
import json
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# लॉगिंग
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token
TOKEN = "8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY"
PORT = int(os.environ.get("PORT", 10000))

# Movies load
try:
    with open("movies.json", "r", encoding="utf-8") as f:
        movies = json.load(f)
    logger.info(f"✅ {len(movies)} movies loaded")
except:
    movies = []
    logger.error("❌ movies.json not found")

def start(update: Update, context: CallbackContext):
    keyboard = [["Bollywood", "Hollywood"], ["South Movies"]]
    update.message.reply_text(
        "🎬 Movie Search Bot\n\nSelect category or type movie name:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def search(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    
    if "bollywood" in text:
        results = [m for m in movies if m.get("category") == "bollywood"]
    elif "hollywood" in text:
        results = [m for m in movies if m.get("category") == "hollywood"]
    elif "south" in text:
        results = [m for m in movies if m.get("category") == "south"]
    else:
        results = [m for m in movies if text in m.get("name", "").lower()]
    
    if results:
        for movie in results[:5]:
            update.message.reply_text(f"🎬 {movie['name']}\n\n📥 {movie['link']}")
    else:
        update.message.reply_text("❌ Not found")

def main():
    # Create updater
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search))
    
    # Start bot
    if os.environ.get("RENDER"):
        # Webhook for Render
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN
        )
        updater.bot.set_webhook(f"https://{os.environ.get('RENDER_EXTERNAL_URL', '')}/{TOKEN}")
        logger.info(f"✅ Bot started on port {PORT}")
    else:
        # Polling for local
        updater.start_polling()
    
    updater.idle()

if __name__ == "__main__":
    main()
