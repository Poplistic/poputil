import sqlite3

db = sqlite3.connect("poputil.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS economy (
    user_id INTEGER,
    guild_id INTEGER,
    balance INTEGER,
    PRIMARY KEY (user_id, guild_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS config (
    guild_id INTEGER PRIMARY KEY,
    welcome_channel INTEGER,
    autorole INTEGER,
    log_channel INTEGER
)
""")

db.commit()
