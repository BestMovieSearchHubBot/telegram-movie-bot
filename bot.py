import os
import json
import logging

# Simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token
TOKEN = "8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY"
PORT = int(os.environ.get("PORT", 10000))

# Import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup

# Load movies
try:
    with open("movies.json", "r", encoding="utf-8") as f:
        movies = json.load(f)
    logger.info(f"✅ Loaded {len(movies)} movies")
except Exception as e:
    logger.error(f"❌ Error: {e}")
    movies = []

def start(update, context):
    """Start command"""
    logger.info(f"User {update.effective_user.first_name} started bot")
    
    keyboard = [
        ["🎬 Bollywood", "🎬 Hollywood"],
        ["🎬 South Movies"]
    ]
    
    update.message.reply_text(
        "Welcome to Movie Search Bot!\n\nSelect category or type movie name:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def search(update, context):
    """Search movies"""
    text = update.message.text.lower()
    logger.info(f"Searching: {text}")
    
    # Remove emoji
    text = text.replace("🎬", "").strip()
    
    # Search
    if "bollywood" in text:
        results = [m for m in movies if m.get("category") == "bollywood"]
        msg = f"Bollywood Movies: {len(results)}"
    elif "hollywood" in text:
        results = [m for m in movies if m.get("category") == "hollywood"]
        msg = f"Hollywood Movies: {len(results)}"
    elif "south" in text:
        results = [m for m in movies if m.get("category") == "south"]
        msg = f"South Movies: {len(results)}"
    else:
        results = [m for m in movies if text in m.get("name", "").lower()]
        msg = f"Found {len(results)} movies"
    
    # Send results
    if results:
        update.message.reply_text(msg)
        for movie in results[:5]:
            update.message.reply_text(
                f"🎬 {movie['name']}\n\n📥 {movie['link']}"
            )
        if len(results) > 5:
            update.message.reply_text(f"Showing 5 of {len(results)} movies")
    else:
        update.message.reply_text("❌ No movies found")

def main():
    """Start bot"""
    logger.info("Starting bot...")
    
    # Create updater
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search))
    
    # Check if on Render
    if os.environ.get("RENDER"):
        logger.info("Running on Render - using webhook")
        
        # Start webhook
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
            logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.info("Running locally - using polling")
        updater.start_polling()
    
    logger.info("Bot is running!")
    updater.idle()

if __name__ == "__main__":
    main()
