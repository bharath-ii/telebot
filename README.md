# 🐹 HamsterTap - Telegram Mini App Bot

A fully operational Telegram Mini App clicker game (HamsterTap) built with HTML5/JS frontend, FastAPI backend, and a `python-telegram-bot` controller.

## 🚀 Features
* **Clicker Game UI:** High-fidelity clicker interface with dynamic upgrades, energy refill, and micro-animations.
* **Persistent DB:** Real-time progress loading and saving of coins, taps, levels, and bought upgrades using SQLite.
* **Live Leaderboards:** Display top rankings in-game or directly in Telegram chat via bot commands.
* **Dynamic Bot Command Interface:** Quick `/score` and `/top` querying directly inside the Telegram conversation.

## 🛠️ Tech Stack
* **Frontend:** Vanilla HTML5, CSS3, ES6 JavaScript, Telegram WebApp SDK
* **Backend:** FastAPI, Python, Uvicorn, SQLite
* **Bot:** Python-Telegram-Bot (V22)

## 📦 Setup & Installation
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn sqlite3 python-telegram-bot
   ```
2. Start the Backend:
   ```bash
   python server.py
   ```
3. Run the Bot:
   ```bash
   python bot.py
   ```
