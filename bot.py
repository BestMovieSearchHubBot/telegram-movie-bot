import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY"
PORT = int(os.environ.get("PORT", 10000))

def start(update, context):
    update.message.reply_text("Hello! Bot is working ✅")

def echo(update, context):
    update.message.reply_text(f"You said: {update.message.text}")

def main():
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    
    if os.environ.get("RENDER"):
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
        updater.bot.set_webhook(f"https://{os.environ['RENDER_EXTERNAL_URL']}/{TOKEN}")
    else:
        updater.start_polling()
    
    updater.idle()

if __name__ == "__main__":
    main()
