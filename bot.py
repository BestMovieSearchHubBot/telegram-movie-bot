import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = "8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY"

with open("movies.json") as f:
    movies = json.load(f)

def start(update: Update, context: CallbackContext):

    keyboard = [
        ["Bollywood", "Hollywood"],
        ["South Movies"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(
        "🎬 Welcome to Movie Search Bot\n\nType movie name to search.",
        reply_markup=reply_markup
    )


def search_movie(update: Update, context: CallbackContext):

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
            update.message.reply_text(
                f"🎬 {movie['name']}\n\nDownload Link:\n{movie['link']}"
            )
    else:
        update.message.reply_text("❌ Movie not found")


def main():

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search_movie))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
