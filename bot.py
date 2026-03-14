import os
import json
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

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
except Exception as e:
    logger.error(f"❌ Error loading movies: {e}")
    movies = []

def start(update, context):
    """Start command"""
    keyboard = [["Bollywood", "Hollywood"], ["South Movies"]]
    update.message.reply_text(
        "🎬 Movie Search Bot\n\nSelect category or type movie name:",
        reply_markup={"keyboard": keyboard, "resize_keyboard": True}
    )
    logger.info("Start command received")

def search(update, context):
    """Search movies"""
    if not movies:
        update.message.reply_text("❌ Database not available")
        return
    
    text = update.message.text.lower()
    logger.info(f"Search: {text}")
    
    # Category search
    if "bollywood" in text:
        results = [m for m in movies if m.get("category") == "bollywood"]
        reply = f"🎬 **Bollywood Movies** ({len(results)} found)\n\n"
    elif "hollywood" in text:
        results = [m for m in movies if m.get("category") == "hollywood"]
        reply = f"🎬 **Hollywood Movies** ({len(results)} found)\n\n"
    elif "south" in text:
        results = [m for m in movies if m.get("category") == "south"]
        reply = f"🎬 **South Movies** ({len(results)} found)\n\n"
    else:
        results = [m for m in movies if text in m.get("name", "").lower()]
        reply = f"🔍 **Search Results** ({len(results)} found)\n\n"
    
    # Send results
    if results:
        for movie in results[:5]:
            update.message.reply_text(
                f"🎬 {movie['name']}\n\n📥 {movie['link']}"
            )
        
        if len(results) > 5:
            update.message.reply_text(f"📌 Showing 5 of {len(results)} movies")
    else:
        update.message.reply_text("❌ No movies found")

def main():
    """Main function"""
    # Create updater
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search))
    
    # Start bot
    if os.environ.get("RENDER"):
        # Webhook for Render
        logger.info("Starting webhook mode...")
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN
        )
        
        # Set webhook
        render_url = os.environ.get("RENDER_EXTERNAL_URL")
        if render_url:
            webhook_url = f"{render_url}/{TOKEN}"
            updater.bot.set_webhook(webhook_url)
            logger.info(f"Webhook set to: {webhook_url}")
    else:
        # Polling for local
        logger.info("Starting polling mode...")
        updater.start_polling()
    
    logger.info("Bot is running...")
    updater.idle()

if __name__ == "__main__":
    main()
