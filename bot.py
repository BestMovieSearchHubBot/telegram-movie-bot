import os
import json
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# लॉगिंग
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Render environment
PORT = int(os.environ.get("PORT", 10000))
TOKEN = os.environ.get("BOT_TOKEN")

# Agar token nahi mila to error do
if not TOKEN:
    logger.error("❌ BOT_TOKEN not found! Please set it in Render Environment Variables")
    # Token hardcode kar do (temporary solution)
    TOKEN = "8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY"
    logger.info("✅ Using hardcoded token (temporary)")

# Movies load karo
try:
    with open("movies.json", "r", encoding="utf-8") as f:
        movies = json.load(f)
    logger.info(f"✅ {len(movies)} movies loaded")
except:
    movies = []
    logger.error("❌ movies.json not found")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Bollywood", "Hollywood"], ["South Movies"]]
    await update.message.reply_text(
        "🎬 Movie Search Bot\n\nSelect category or type movie name:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await update.message.reply_text(f"{movie['name']}\n\n📥 {movie['link']}")
    else:
        await update.message.reply_text("❌ Not found")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    
    # Production mein webhook
    if os.environ.get("RENDER"):
        render_url = os.environ.get("RENDER_EXTERNAL_URL")
        if render_url:
            app.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN,
                webhook_url=f"{render_url}/{TOKEN}"
            )
    else:
        # Local mein polling
        app.run_polling()

if __name__ == "__main__":
    main()
