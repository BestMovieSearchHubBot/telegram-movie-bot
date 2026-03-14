import json
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Token ko environment variable se lena safe hota hai
TOKEN = os.environ.get("BOT_TOKEN", "8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY")

# Load movies with error handling
try:
    with open("movies.json", "r") as f:
        movies = json.load(f)
except FileNotFoundError:
    movies = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Bollywood", "Hollywood"],
        ["South Movies"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🎬 Welcome to Movie Search Bot\n\nType movie name to search.",
        reply_markup=reply_markup
    )

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # Category checking logic
    if text == "bollywood":
        result = [m for m in movies if m["category"].lower() == "bollywood"]
    elif text == "hollywood":
        result = [m for m in movies if m["category"].lower() == "hollywood"]
    elif text == "south movies":
        result = [m for m in movies if m["category"].lower() == "south"]
    else:
        result = [m for m in movies if text in m["name"].lower()]

    if result:
        # Limit results to 5 to avoid flooding/spam
        for movie in result[:5]:
            await update.message.reply_text(
                f"🎬 *{movie['name']}*\n\n📥 [Download Link]({movie['link']})",
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text("❌ Movie not found")

def main():
    if not TOKEN:
        print("Error: No Token found!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))

    print("Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
