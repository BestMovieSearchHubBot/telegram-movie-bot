# 🎬 Telegram Movie Search Bot

A powerful Telegram bot for searching movies and getting download links.

## ✨ Features

- 🔍 Search movies by name
- 🎯 Browse by categories (Bollywood, Hollywood, South)
- 📥 Direct download links
- 🚀 Fast and responsive
- 🌐 Deployed on Render

## 📋 Categories

- **Bollywood** - Hindi Movies
- **Hollywood** - English Movies
- **South Movies** - South Indian Movies

## 🚀 Deploy on Render

### Step 1: Fork this repository

### Step 2: Create a new Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Fill the details:
   - **Name**: `telegram-movie-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn bot:flask_app`

### Step 3: Add Environment Variables

Add these in Render dashboard:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | `8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY` |
| `RENDER_EXTERNAL_URL` | `https://telegram-movie-bot-mw26.onrender.com` |
### Step 4: Set Webhook

After deployment, run this in browser:
