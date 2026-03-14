const { Telegraf, Markup } = require('telegraf');
const express = require('express');
const fs = require('fs').promises;

const app = express();
const PORT = process.env.PORT || 3000;

// Express server for Render health check
app.get('/', (req, res) => res.send('Movie Bot is Live!'));
app.get('/ping', (req, res) => res.status(200).send('OK'));
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

// Bot token (aapka wala)
const bot = new Telegraf('8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY');

// Movies data (JSON file se load karenge)
let movies = [];

// Load movies on startup
async function loadMovies() {
    try {
        const data = await fs.readFile('movies.json', 'utf8');
        movies = JSON.parse(data);
        console.log(`✅ ${movies.length} movies loaded`);
    } catch (error) {
        console.error('❌ Error loading movies:', error.message);
        movies = [];
    }
}
loadMovies();

// /start command
bot.start(async (ctx) => {
    const firstName = ctx.from.first_name || "User";
    
    const welcomeMessage = `🎬 **Hi ${firstName}, Welcome to Movie Search Bot!**\n\n` +
        `Search movies by:\n` +
        `• Category: Bollywood, Hollywood, South\n` +
        `• Movie name (e.g., Pathaan, KGF)\n\n` +
        `👇 **Choose a category below or type any movie name!**`;

    // Keyboard with categories
    const keyboard = Markup.keyboard([
        ['🎬 Bollywood', '🎬 Hollywood'],
        ['🎬 South Movies']
    ]).resize();

    await ctx.replyWithMarkdown(welcomeMessage, keyboard);
});

// Handle text messages
bot.on('text', async (ctx) => {
    const text = ctx.message.text.toLowerCase().replace('🎬', '').trim();
    let results = [];

    // Category search
    if (text.includes('bollywood')) {
        results = movies.filter(m => m.category === 'bollywood');
        await ctx.reply(`🎬 *Bollywood Movies* (${results.length} found)`, { parse_mode: 'Markdown' });
    }
    else if (text.includes('hollywood')) {
        results = movies.filter(m => m.category === 'hollywood');
        await ctx.reply(`🎬 *Hollywood Movies* (${results.length} found)`, { parse_mode: 'Markdown' });
    }
    else if (text.includes('south')) {
        results = movies.filter(m => m.category === 'south');
        await ctx.reply(`🎬 *South Movies* (${results.length} found)`, { parse_mode: 'Markdown' });
    }
    else {
        // Normal search by name
        results = movies.filter(m => m.name.toLowerCase().includes(text));
        await ctx.reply(`🔍 *${results.length} movies found* for "${ctx.message.text}"`, { parse_mode: 'Markdown' });
    }

    // Send results (max 5)
    if (results.length > 0) {
        for (const movie of results.slice(0, 5)) {
            const msg = `🎬 *${movie.name}*\n📥 [Download Link](${movie.link})`;
            await ctx.replyWithMarkdown(msg, { disable_web_page_preview: false });
        }
        if (results.length > 5) {
            await ctx.reply(`📌 Showing 5 of ${results.length} movies. Try more specific search.`);
        }
    } else {
        await ctx.reply('❌ No movies found. Try another name or category.');
    }
});

// Bot launch
bot.launch().then(() => console.log('🤖 Movie Bot started!'));

// Graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
