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

// Movies data – now with poster and quality fields
let movies = [];

async function loadMovies() {
    try {
        const data = await fs.readFile('movies.json', 'utf8');
        movies = JSON.parse(data);
        console.log(`✅ ${movies.length} movies loaded`);
        // Optional: validate each movie has required fields
    } catch (error) {
        console.error('❌ Error loading movies:', error.message);
        movies = [];
    }
}
loadMovies();

// /start command – Simple welcome without keyboard
bot.start(async (ctx) => {
    const firstName = ctx.from.first_name || 'User';
    const welcomeMessage = `🎬 *Welcome ${firstName}!*\n\n` +
        `🔍 Just type any movie name (e.g., *Pathaan*, *KGF*, *Inception*) and I'll send you the download link with poster and quality details.\n\n` +
        `✨ *Fast • Easy • Professional*`;
    await ctx.replyWithMarkdown(welcomeMessage);
});

// Handle text messages – Search only
bot.on('text', async (ctx) => {
    if (!movies.length) {
        return ctx.reply('❌ *Database not available. Try later!*', { parse_mode: 'Markdown' });
    }

    const query = ctx.message.text.trim().toLowerCase();
    if (!query) return;

    // Search movies by name (case-insensitive)
    const results = movies.filter(m => m.name.toLowerCase().includes(query));

    if (results.length === 0) {
        return ctx.replyWithMarkdown(
            `❌ *No movies found for* "${ctx.message.text}"\n\n` +
            `💡 Try a different spelling or check the movie name.`
        );
    }

    // Limit to first 5 results to avoid spam
    const limited = results.slice(0, 5);
    let sentCount = 0;

    for (const movie of limited) {
        // Prepare caption with movie details
        const caption = 
            `🎬 *${movie.name}*\n` +
            `📂 *Category:* ${movie.category.charAt(0).toUpperCase() + movie.category.slice(1)}\n` +
            `⚙️ *Quality:* ${movie.quality || 'N/A'}\n\n` +
            `⬇️ Click the button below to download.`;

        // If poster URL exists, send photo; otherwise send text
        if (movie.poster) {
            try {
                await ctx.replyWithPhoto(movie.poster, {
                    caption,
                    parse_mode: 'Markdown',
                    ...Markup.inlineKeyboard([
                        [Markup.button.url('📥 Download Now', movie.link)]
                    ])
                });
                sentCount++;
            } catch (err) {
                // Fallback if photo fails (invalid URL, etc.)
                await ctx.replyWithMarkdown(caption, {
                    ...Markup.inlineKeyboard([
                        [Markup.button.url('📥 Download Now', movie.link)]
                    ])
                });
                sentCount++;
            }
        } else {
            // No poster – send text only
            await ctx.replyWithMarkdown(caption, {
                ...Markup.inlineKeyboard([
                    [Markup.button.url('📥 Download Now', movie.link)]
                ])
            });
            sentCount++;
        }

        // Small delay to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 300));
    }

    // If there are more movies than shown
    if (results.length > 5) {
        await ctx.replyWithMarkdown(
            `📌 *Showing ${sentCount} of ${results.length} movies.*\n` +
            `✨ Type a more specific name to narrow down results.`
        );
    }
});

// Bot launch
bot.launch().then(() => console.log('🤖 Movie Bot started successfully!'));

// Graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
