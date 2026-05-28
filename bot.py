"""
HamsterTap Bot - Telegram Mini App Game Bot
Run: pip install python-telegram-bot
Then: python bot.py
"""

import logging
import os
import sqlite3
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load local .env file if present
load_dotenv()

# =============================================
# CONFIG — Replace these with your values!
# =============================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")             # Set in .env or cloud hosting dashboard
GAME_URL = os.getenv("GAME_URL", "http://localhost:8000/static/index.html")  # Set in .env or cloud hosting dashboard
# =============================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with Play button"""
    user = update.effective_user
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🐹 Play HamsterTap!",
            web_app=WebAppInfo(url=GAME_URL)
        )
    ]])
    await update.message.reply_text(
        f"👋 Hey {user.first_name}!\n\n"
        f"🐹 Welcome to *HamsterTap* — tap your way to riches!\n\n"
        f"⚡ Tap the hamster to earn coins\n"
        f"🛒 Buy upgrades to tap faster\n"
        f"🏆 Compete on the leaderboard\n"
        f"📺 Watch ads to refill energy\n\n"
        f"👇 Tap the button to start playing!",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 *HamsterTap Help*\n\n"
        "/start - Launch the game\n"
        "/score - Check your score\n"
        "/top - View leaderboard\n"
        "/help - Show this help\n\n"
        "💡 *Tips:*\n"
        "• Buy upgrades to earn more coins per tap\n"
        "• Watch ads to refill energy for free\n"
        "• Invite friends for bonus coins!",
        parse_mode="Markdown"
    )


async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's score (fetched from backend SQLite)"""
    user_id = update.effective_user.id
    try:
        conn = sqlite3.connect("game.db")
        c = conn.cursor()
        c.execute("SELECT score, level, taps FROM scores WHERE user_id=?", (str(user_id),))
        row = c.fetchone()
        conn.close()
    except Exception as e:
        row = None
        logger.error(f"Error reading database: {e}")

    if row:
        score, level, taps = row
        await update.message.reply_text(
            f"🎮 *Your HamsterTap Progress*\n\n"
            f"🪙 *Score:* {score:,} coins\n"
            f"⚡ *Level:* {level}\n"
            f"💥 *Total Taps:* {taps:,}\n\n"
            f"Keep tapping to reach the top!",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"🪙 You haven't started playing yet, {update.effective_user.first_name}!\n\n"
            f"Use /start to launch the game.",
        )


async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top players dynamically"""
    try:
        conn = sqlite3.connect("game.db")
        c = conn.cursor()
        c.execute("SELECT username, score FROM scores ORDER BY score DESC LIMIT 10")
        rows = c.fetchall()
        conn.close()
    except Exception as e:
        rows = []
        logger.error(f"Error reading database: {e}")

    if rows:
        text = "🏆 *Top Players (Live)*\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, r in enumerate(rows):
            username, score = r
            medal = medals[i] if i < 3 else f"{i+1}."
            text += f"{medal} *{username}* — {score:,} coins\n"
        text += "\n_Play more to get on this list!_"
    else:
        text = "🏆 *Leaderboard is currently empty!*\n\nBe the first to tap and claim the top spot using /start!"

    await update.message.reply_text(text, parse_mode="Markdown")


async def share_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Invite friends"""
    bot_username = context.bot.username
    invite_link = f"https://t.me/{bot_username}?start=ref_{update.effective_user.id}"
    await update.message.reply_text(
        f"🎁 *Invite Friends & Earn!*\n\n"
        f"Share your link:\n`{invite_link}`\n\n"
        f"You earn *500 bonus coins* for each friend who joins! 🎉",
        parse_mode="Markdown"
    )


def main():
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("score", score_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("share", share_command))

    print("🐹 HamsterTap Bot is running!")
    print(f"🌐 Game URL: {GAME_URL}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
