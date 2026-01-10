import sqlite3

db = sqlite3.connect("poputil.db", check_same_thread=False)
cursor = db.cursor()

# Economy table
cursor.execute("""
CREATE TABLE IF NOT EXISTS economy (
    user_id INTEGER,
    guild_id INTEGER,
    balance INTEGER DEFAULT 0,
    last_daily INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, guild_id)
)
""")

# Server config table
cursor.execute("""
CREATE TABLE IF NOT EXISTS config (
    guild_id INTEGER PRIMARY KEY,
    welcome_channel INTEGER,
    autorole INTEGER
)
""")

db.commit()
