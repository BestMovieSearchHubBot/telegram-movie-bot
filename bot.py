import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY"

with open("movies.json") as f:
    movies = json.load(f)


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

    if text == "bollywood":
        result = [m for m in movies if m["category"] == "bollywood"]

    elif text == "hollywood":
        result = [m for m in movies if m["category"] == "hollywood"]

    elif text == "south movies":
        result = [m for m in movies if m["category"] == "south"]

    else:
        result = [m for m in movies if text in m["name"].lower()]

    if result:
        for movie in result[:10]:
            await update.message.reply_text(
                f"🎬 {movie['name']}\n\nDownload Link:\n{movie['link']}"
            )
    else:
        await update.message.reply_text("❌ Movie not found")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))

    print("Bot Running...")

    app.run_polling()


if __name__ == "__main__":
    main()
