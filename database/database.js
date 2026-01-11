const Database = require('better-sqlite3');
const db = new Database('/data/poputil.db');

db.prepare(`
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT,
    guild_id TEXT,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    balance INTEGER DEFAULT 0,
    last_daily INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, guild_id)
)`).run();

db.prepare(`
CREATE TABLE IF NOT EXISTS guilds (
    guild_id TEXT PRIMARY KEY,
    xp_enabled INTEGER DEFAULT 1,
    xp_rate INTEGER DEFAULT 10
)`).run();

db.prepare(`
CREATE TABLE IF NOT EXISTS inventory (
    user_id TEXT,
    guild_id TEXT,
    item TEXT,
    amount INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, guild_id, item)
)`).run();

db.prepare(`
CREATE TABLE IF NOT EXISTS shop (
    item TEXT PRIMARY KEY,
    price INTEGER
)`).run();

/* Default shop items */
const items = [
    ['cookie', 50],
['rolepass', 250],
['lottery', 500]
];

for (const [item, price] of items) {
    db.prepare(`
    INSERT OR IGNORE INTO shop (item, price)
    VALUES (?, ?)
    `).run(item, price);
}

module.exports = db;
