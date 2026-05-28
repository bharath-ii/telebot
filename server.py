"""
HamsterTap Backend Server
Handles score saving, leaderboard, user data

Run:
  pip install fastapi uvicorn sqlite3
  python server.py
"""

import sqlite3
import hashlib
import hmac
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# =============================================
# CONFIG
# =============================================
BOT_TOKEN = "8222112664:AAF66DPzVakaMYvJNT_D3rmi3OiqBy4krVs"   # Same as in bot.py
DB_FILE = "game.db"
# =============================================

app = FastAPI(title="HamsterTap API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the game files (index.html)
app.mount("/static", StaticFiles(directory="."), name="static")


# ========== DATABASE ==========
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            score INTEGER DEFAULT 0,
            taps INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            upgrades TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Add upgrades column if table exists without it
    try:
        c.execute("ALTER TABLE scores ADD COLUMN upgrades TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

init_db()


def get_db():
    return sqlite3.connect(DB_FILE)


# ========== TELEGRAM VALIDATION ==========
def validate_telegram_data(init_data: str) -> bool:
    """Verify the request is from real Telegram"""
    if not init_data:
        return False  # Allow in dev mode; set True in production
    try:
        data_dict = {}
        for chunk in init_data.split("&"):
            key, val = chunk.split("=", 1)
            data_dict[key] = val

        hash_val = data_dict.pop("hash", "")
        data_check = "\n".join(
            f"{k}={v}" for k, v in sorted(data_dict.items())
        )

        secret = hmac.new(
            b"WebAppData",
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        expected = hmac.new(
            secret,
            data_check.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, hash_val)
    except Exception:
        return False


# ========== MODELS ==========
class ScoreUpdate(BaseModel):
    user_id: str
    username: str
    score: int
    taps: Optional[int] = 0
    level: Optional[int] = 1
    upgrades: Optional[str] = ""
    init_data: Optional[str] = ""


# ========== ROUTES ==========
@app.get("/")
def root():
    return {"status": "HamsterTap API running 🐹"}


@app.post("/api/score")
def save_score(data: ScoreUpdate):
    """Save or update a player's score"""
    # Validate in production:
    # if not validate_telegram_data(data.init_data):
    #     raise HTTPException(status_code=403, detail="Invalid Telegram data")

    conn = get_db()
    c = conn.cursor()

    # Only update if new score is higher
    c.execute("""
        INSERT INTO scores (user_id, username, score, taps, level, upgrades)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            score = MAX(score, excluded.score),
            taps = taps + excluded.taps,
            level = excluded.level,
            upgrades = excluded.upgrades,
            updated_at = CURRENT_TIMESTAMP
    """, (data.user_id, data.username, data.score, data.taps, data.level, data.upgrades))

    conn.commit()
    conn.close()
    return {"status": "ok"}


@app.get("/api/score/{user_id}")
def get_score(user_id: str):
    """Get a player's score"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT user_id, username, score, taps, level, upgrades 
        FROM scores 
        WHERE user_id=?
    """, (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return {"user_id": user_id, "score": 0, "level": 1, "taps": 0, "upgrades": ""}

    return {
        "user_id": row[0],
        "username": row[1],
        "score": row[2],
        "taps": row[3],
        "level": row[4],
        "upgrades": row[5]
    }


@app.get("/api/leaderboard")
def get_leaderboard(limit: int = 10):
    """Get top players"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT user_id, username, score, level
        FROM scores
        ORDER BY score DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()

    return {
        "leaderboard": [
            {"rank": i+1, "user_id": r[0], "username": r[1], "score": r[2], "level": r[3]}
            for i, r in enumerate(rows)
        ]
    }


@app.get("/api/rank/{user_id}")
def get_rank(user_id: str):
    """Get a player's rank"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) FROM scores
        WHERE score > (SELECT score FROM scores WHERE user_id=?)
    """, (user_id,))
    rank = c.fetchone()[0] + 1
    conn.close()
    return {"user_id": user_id, "rank": rank}


# ========== RUN ==========
if __name__ == "__main__":
    import uvicorn
    print("🐹 HamsterTap Server starting...")
    print("📡 API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
