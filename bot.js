const { Telegraf, Markup } = require('telegraf');
const express = require('express');
const fs = require('fs').promises;

const app = express();
const PORT = process.env.PORT || 3000;

// Express server for Render health check
app.get('/', (req, res) => res.send('🎬 Movie Bot is Live!'));
app.get('/ping', (req, res) => res.status(200).send('OK'));
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));

// Bot token
const bot = new Telegraf('8786374300:AAGlF27oE0rwCwRPhwrDkt-mEt5C6f4H9eY');

// Movies data
let movies = [];

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

// /start command – Professional welcome
bot.start(async (ctx) => {
    const firstName = ctx.from.first_name || 'User';
    
    const welcomeMessage = `🎬 **Welcome ${firstName}!**\n\n` +
        `🔍 **Movie Search Bot** – Find any movie instantly!\n\n` +
        `📌 **How to use:**\n` +
        `• Tap on category buttons below\n` +
        `• Type movie name (e.g., Pathaan, KGF)\n` +
        `• Get download link instantly\n\n` +
        `👇 **Choose a category:**`;

    const keyboard = Markup.keyboard([
        ['🎬 Bollywood', '🎬 Hollywood'],
        ['🎬 South Movies']
    ]).resize();

    await ctx.replyWithMarkdown(welcomeMessage, keyboard);
});

// Handle text messages – Attractive output
bot.on('text', async (ctx) => {
    if (!movies.length) {
        return ctx.reply('❌ *Database not available. Try later!*', { parse_mode: 'Markdown' });
    }

    const text = ctx.message.text.toLowerCase().replace('🎬', '').trim();
    let results = [];
    let category = '';

    // Category search
    if (text.includes('bollywood')) {
        results = movies.filter(m => m.category === 'bollywood');
        category = 'Bollywood';
    } else if (text.includes('hollywood')) {
        results = movies.filter(m => m.category === 'hollywood');
        category = 'Hollywood';
    } else if (text.includes('south')) {
        results = movies.filter(m => m.category === 'south');
        category = 'South';
    } else {
        results = movies.filter(m => m.name.toLowerCase().includes(text));
    }

    // If no results
    if (results.length === 0) {
        return ctx.replyWithMarkdown(
            `❌ *No movies found for* "${ctx.message.text}"\n\n` +
            `💡 Try different spelling or use category buttons.`
        );
    }

    // Category header
    if (category) {
        await ctx.replyWithMarkdown(
            `🎬 *${category} Movies* (${results.length} found)\n═══════════════════`
        );
    } else {
        await ctx.replyWithMarkdown(
            `🔍 *${results.length} movies found* for "${ctx.message.text}"\n═══════════════════`
        );
    }

    // Send each movie as a card
    for (const movie of results.slice(0, 5)) {
        const message = `🎥 *${movie.name}*\n` +
                       `📂 *Category:* ${movie.category.charAt(0).toUpperCase() + movie.category.slice(1)}\n\n` +
                       `📥 **Download:**`;

        await ctx.replyWithMarkdown(message, {
            ...Markup.inlineKeyboard([
                [Markup.button.url('⬇️ Get Link', movie.link)]
            ])
        });
    }

    // If more than 5 movies
    if (results.length > 5) {
        await ctx.replyWithMarkdown(
            `📌 *Showing 5 of ${results.length} movies.*\n` +
            `✨ Type exact name for more specific results.`
        );
    }
});

// Bot launch
bot.launch().then(() => console.log('🤖 Movie Bot started successfully!'));

// Graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
