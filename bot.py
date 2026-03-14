import os
import json
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request
import asyncio

# लॉगिंग सेटअप
logging.basicConfig(
    format='%(asame)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# टोकन और पोर्ट सेटिंग
TOKEN = os.environ.get("BOT_TOKEN", "8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY")
PORT = int(os.environ.get("PORT", 10000))

# Flask ऐप
flask_app = Flask(__name__)

# movies.json लोड करें
try:
    with open("movies.json", "r", encoding="utf-8") as f:
        movies = json.load(f)
    logger.info(f"✅ {len(movies)} movies loaded successfully")
except FileNotFoundError:
    logger.error("❌ movies.json file not found!")
    movies = []
except json.JSONDecodeError:
    logger.error("❌ movies.json is corrupted!")
    movies = []

# ग्लोबल वेरिएबल for application
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
    
    welcome_message = f"""🎬 Welcome {user.first_name} to Movie Search Bot!

🔍 How to use:
• Click on category buttons
• Or type any movie name

📽️ Categories:
• Bollywood
• Hollywood
• South Movies

Enjoy your movies! 🍿"""
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search movies based on user input"""
    
    # Check if movies database is loaded
    if not movies:
        await update.message.reply_text("❌ Database not available. Please try again later.")
        return
    
    # Get user message
    text = update.message.text.strip()
    original_text = text
    text_lower = text.lower()
    
    logger.info(f"Search query: {text}")
    
    # Remove emoji if present
    if "🎬" in text:
        text_lower = text_lower.replace("🎬", "").strip()
    
    # Category search
    if "bollywood" in text_lower:
        result = [m for m in movies if m.get("category", "").lower() == "bollywood"]
        category_name = "Bollywood"
    elif "hollywood" in text_lower:
        result = [m for m in movies if m.get("category", "").lower() == "hollywood"]
        category_name = "Hollywood"
    elif "south" in text_lower:
        result = [m for m in movies if m.get("category", "").lower() == "south"]
        category_name = "South Movies"
    else:
        # Normal search
        result = [m for m in movies if text_lower in m.get("name", "").lower()]
        category_name = None
    
    # Send results
    if result:
        if category_name:
            await update.message.reply_text(f"📽️ **{category_name} Movies Found:** {len(result)}")
        else:
            await update.message.reply_text(f"🔍 Found {len(result)} movies matching '{original_text}'")
        
        # Send movies (limit to 5 to avoid spam)
        sent_count = 0
        for movie in result[:5]:
            try:
                movie_name = movie.get("name", "Unknown")
                movie_link = movie.get("link", "#")
                
                message = f"""🎬 **{movie_name}**

📥 **Download Link:**
{movie_link}

⭐ Enjoy the movie!"""
                
                await update.message.reply_text(
                    message,
                    disable_web_page_preview=False
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Error sending movie: {e}")
        
        if len(result) > 5:
            await update.message.reply_text(f"📌 Showing 5 of {len(result)} movies. Please refine your search for more specific results.")
    else:
        await update.message.reply_text(
            f"❌ No movies found matching '{original_text}'\n\n"
            "Try:\n"
            "• Using category buttons\n"
            "• Checking spelling\n"
            "• Searching with different keywords"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = """📖 **Movie Search Bot Help**

**Commands:**
/start - Start the bot
/help - Show this help
/categories - Show all categories

**How to Search:**
1. Click on category buttons
2. Type any movie name
3. Use keywords

**Categories:**
• Bollywood - Hindi movies
• Hollywood - English movies
• South Movies - South Indian movies

**Support:**
If you find any issues, please try again later.

Happy Watching! 🍿"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all categories"""
    # Get unique categories
    categories = set(m.get("category", "").lower() for m in movies if m.get("category"))
    
    message = "**📽️ Available Categories:**\n\n"
    
    for category in categories:
        count = len([m for m in movies if m.get("category", "").lower() == category])
        message += f"• **{category.title()}** - {count} movies\n"
    
    message += "\nClick on category buttons to browse!"
    
    await update.message.reply_text(message, parse_mode='Markdown')

# Flask webhook endpoint
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Handle Telegram webhook updates"""
    if request.method == "POST":
        try:
            update = Update.de_json(request.get_json(force=True), application.bot)
            asyncio.run_coroutine_threadsafe(application.process_update(update), application.loop)
            return "OK", 200
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return "Error", 500

@flask_app.route("/")
def index():
    """Health check endpoint"""
    return "🤖 Movie Search Bot is running!", 200

@flask_app.route("/health")
def health():
    """Health check for Render"""
    return {"status": "healthy", "movies_count": len(movies)}, 200

def setup_webhook(application):
    """Setup webhook for the bot"""
    try:
        # Get Render URL
        render_url = os.environ.get("RENDER_EXTERNAL_URL")
        
        if render_url:
            webhook_url = f"{render_url}/{TOKEN}"
            
            # Delete old webhook
            application.bot.delete_webhook()
            
            # Set new webhook
            success = application.bot.set_webhook(url=webhook_url)
            
            if success:
                logger.info(f"✅ Webhook set successfully to: {webhook_url}")
                
                # Get webhook info
                webhook_info = application.bot.get_webhook_info()
                logger.info(f"Webhook info: {webhook_info}")
            else:
                logger.error("❌ Failed to set webhook")
        else:
            logger.warning("⚠️ RENDER_EXTERNAL_URL not set, using polling")
            application.run_polling()
            
    except Exception as e:
        logger.error(f"❌ Webhook setup failed: {e}")
        logger.info("Falling back to polling mode")
        application.run_polling()

def main():
    """Main function to run the bot"""
    global application
    
    try:
        # Create application
        logger.info("🚀 Starting Movie Search Bot...")
        
        # Build application
        builder = Application.builder().token(TOKEN)
        
        # Add timeouts
        builder.connect_timeout(30)
        builder.read_timeout(30)
        builder.write_timeout(30)
        
        application = builder.build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("categories", categories_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))
        
        logger.info("✅ Handlers added successfully")
        
        # Check if running on Render
        if os.environ.get("RENDER"):
            logger.info("🌐 Running on Render, setting up webhook...")
            setup_webhook(application)
            
            # Run Flask app
            logger.info(f"🚀 Flask server starting on port {PORT}")
            flask_app.run(host="0.0.0.0", port=PORT)
        else:
            # Local development - use polling
            logger.info("💻 Running locally, using polling...")
            application.run_polling()
            
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        raise

if __name__ == "__main__":
    main()
