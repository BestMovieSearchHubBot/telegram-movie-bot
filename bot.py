import os
import json
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request
import asyncio

# लॉगिंग सेटअप
logging.basicConfig(
    format='%(asime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

if not TOKEN:
    logger.error("❌ BOT_TOKEN not set in environment variables!")
    exit(1)

# Flask ऐप
flask_app = Flask(__name__)

# movies.json लोड करें
def load_movies():
    try:
        with open("movies.json", "r", encoding="utf-8") as f:
            movies_data = json.load(f)
        logger.info(f"✅ {len(movies_data)} movies loaded successfully")
        return movies_data
    except FileNotFoundError:
        logger.error("❌ movies.json file not found!")
        return []
    except json.JSONDecodeError:
        logger.error("❌ movies.json is corrupted!")
        return []

movies = load_movies()

# Initialize bot application
application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    
    # Keyboard buttons
    keyboard = [
        ["🎬 Bollywood", "🎬 Hollywood"],
        ["🎬 South Movies"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_message = f"""🎬 **Welcome {user.first_name} to Movie Search Bot!**

🔍 **How to use:**
• Click on category buttons below
• Or type any movie name directly

📽️ **Available Categories:**
• Bollywood - {len([m for m in movies if m.get('category')=='bollywood'])} movies
• Hollywood - {len([m for m in movies if m.get('category')=='hollywood'])} movies
• South Movies - {len([m for m in movies if m.get('category')=='south'])} movies

**Commands:**
/help - Show help
/categories - Browse categories

Enjoy your movies! 🍿"""
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    logger.info(f"User {user.first_name} started the bot")

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search movies based on user input"""
    
    if not movies:
        await update.message.reply_text("❌ Database not available. Please try again later.")
        return
    
    text = update.message.text.strip()
    original_text = text
    text_lower = text.lower()
    
    logger.info(f"Search query from {update.effective_user.first_name}: {text}")
    
    # Remove emoji if present
    text_lower = text_lower.replace("🎬", "").strip()
    
    # Search by category or name
    if text_lower in ["bollywood", "hollywood", "south movies", "south"]:
        if "bollywood" in text_lower:
            category = "bollywood"
            display_name = "Bollywood"
        elif "hollywood" in text_lower:
            category = "hollywood"
            display_name = "Hollywood"
        else:  # south
            category = "south"
            display_name = "South Movies"
        
        results = [m for m in movies if m.get("category", "").lower() == category]
        await update.message.reply_text(f"🎯 Found {len(results)} {display_name} movies:")
    else:
        # Search by movie name
        results = [m for m in movies if text_lower in m.get("name", "").lower()]
        await update.message.reply_text(f"🔍 Found {len(results)} movies matching '{original_text}':")
    
    # Send results (max 5)
    if results:
        for movie in results[:5]:
            try:
                name = movie.get("name", "Unknown")
                quality = movie.get("quality", "HD")
                year = movie.get("year", "N/A")
                link = movie.get("link", "#")
                
                message = f"""🎬 **{name}**
📅 Year: {year}
✨ Quality: {quality}

📥 **Download:** [Click Here]({link})"""
                
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
            except Exception as e:
                logger.error(f"Error sending movie: {e}")
        
        if len(results) > 5:
            await update.message.reply_text(f"📌 Showing 5 of {len(results)} movies. Try more specific search.")
    else:
        await update.message.reply_text(
            f"❌ No movies found matching '{original_text}'\n\n"
            "💡 **Tips:**\n"
            "• Try different spelling\n"
            "• Use category buttons\n"
            "• Search for partial names"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = """📖 **Movie Search Bot Help**

**Commands:**
/start - Start the bot
/help - Show this help
/categories - List all categories

**Search Tips:**
1. Click category buttons for lists
2. Type movie name for specific search
3. Partial names work too!

**Categories:**
• Bollywood (Hindi Movies)
• Hollywood (English Movies)
• South Movies (Tamil, Telugu, Kannada)

**Support:**
If bot doesn't respond, try /start again

Happy Watching! 🍿"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all categories with counts"""
    categories = {
        "bollywood": "Bollywood",
        "hollywood": "Hollywood", 
        "south": "South Movies"
    }
    
    message = "**📽️ Movie Categories**\n\n"
    
    for cat_key, cat_name in categories.items():
        count = len([m for m in movies if m.get("category", "").lower() == cat_key])
        message += f"• **{cat_name}**: {count} movies\n"
    
    message += "\nClick on category buttons below to browse!"
    
    await update.message.reply_text(message, parse_mode='Markdown')

# Flask routes
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Handle Telegram updates"""
    if application is None:
        return "Application not initialized", 500
    
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run_coroutine_threadsafe(application.process_update(update), application.loop)
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

@flask_app.route("/")
def index():
    """Home page"""
    return """
    <html>
        <head><title>Movie Search Bot</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🤖 Movie Search Bot</h1>
            <p>Bot is running successfully!</p>
            <p>📊 Movies in database: {}</p>
            <p><a href="https://t.me/{}">Open Bot in Telegram</a></p>
        </body>
    </html>
    """.format(len(movies), "YOUR_BOT_USERNAME")

@flask_app.route("/health")
def health():
    """Health check"""
    return {
        "status": "healthy",
        "movies_count": len(movies),
        "bot_initialized": application is not None
    }

@flask_app.route("/debug")
def debug():
    """Debug info"""
    return {
        "bot_token_set": bool(TOKEN),
        "movies_count": len(movies),
        "port": PORT,
        "webhook_url": f"https://{request.host}/{TOKEN}"
    }

def setup_webhook():
    """Setup webhook for production"""
    global application
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("categories", categories_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))
    
    logger.info("✅ Bot handlers added")
    
    # Setup webhook
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    
    if render_url:
        webhook_url = f"{render_url}/{TOKEN}"
        logger.info(f"Setting webhook to: {webhook_url}")
        
        try:
            # Delete old webhook
            application.bot.delete_webhook()
            logger.info("✅ Old webhook deleted")
            
            # Set new webhook
            success = application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=["message", "callback_query"]
            )
            
            if success:
                logger.info(f"✅ Webhook set successfully to: {webhook_url}")
                
                # Verify webhook
                webhook_info = application.bot.get_webhook_info()
                logger.info(f"Webhook info: {webhook_info}")
                
                return True
            else:
                logger.error("❌ Failed to set webhook")
                return False
        except Exception as e:
            logger.error(f"❌ Webhook setup error: {e}")
            return False
    else:
        logger.error("❌ RENDER_EXTERNAL_URL not set!")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting Movie Search Bot...")
    
    # Setup bot and webhook
    if setup_webhook():
        logger.info(f"✅ Bot ready! Listening on port {PORT}")
        
        # Run Flask app
        flask_app.run(
            host="0.0.0.0",
            port=PORT,
            debug=False
        )
    else:
        logger.error("❌ Failed to setup webhook. Check your environment variables.")
