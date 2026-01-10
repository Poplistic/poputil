import sqlite3

db = sqlite3.connect("poputil.db", check_same_thread=False)
cursor = db.cursor()

# Economy
cursor.execute("""
CREATE TABLE IF NOT EXISTS economy (
    user_id INTEGER,
    guild_id INTEGER,
    balance INTEGER DEFAULT 0,
    last_daily INTEGER DEFAULT 0,
    last_work INTEGER DEFAULT 0,
    last_crime INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, guild_id)
)
""")

# Inventory
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    user_id INTEGER,
    guild_id INTEGER,
    item TEXT,
    amount INTEGER,
    PRIMARY KEY (user_id, guild_id, item)
)
""")

# Server config
cursor.execute("""
CREATE TABLE IF NOT EXISTS config (
    guild_id INTEGER PRIMARY KEY,
    welcome_channel INTEGER,
    autorole INTEGER
)
""")

db.commit()
