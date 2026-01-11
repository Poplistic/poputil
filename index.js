const fs = require('fs');
const path = require('path');
const express = require('express');
const { Client, Collection, GatewayIntentBits } = require('discord.js');
const db = require('./database/database');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers
    ]
});

client.commands = new Collection();

/* Load commands */
for (const file of fs.readdirSync('./commands')) {
    const cmd = require(`./commands/${file}`);
    client.commands.set(cmd.data.name, cmd);
}

/* Ready */
client.once('ready', () => {
    console.log(`PopUtil online as ${client.user.tag}`);
});

/* Slash commands */
client.on('interactionCreate', async i => {
    if (!i.isChatInputCommand()) return;
    const cmd = client.commands.get(i.commandName);
    if (cmd) await cmd.execute(i);
});

/* XP SYSTEM */
client.on('messageCreate', msg => {
    if (!msg.guild || msg.author.bot) return;

    db.prepare(`INSERT OR IGNORE INTO guilds (guild_id) VALUES (?)`)
    .run(msg.guild.id);

    const guild = db.prepare(
        `SELECT * FROM guilds WHERE guild_id = ?`
    ).get(msg.guild.id);

    if (!guild.xp_enabled) return;

    const xpGain = Math.floor(Math.random() * guild.xp_rate) + 1;

    db.prepare(`
    INSERT OR IGNORE INTO users (user_id, guild_id)
    VALUES (?, ?)
    `).run(msg.author.id, msg.guild.id);

    const user = db.prepare(`
    SELECT * FROM users WHERE user_id = ? AND guild_id = ?
    `).get(msg.author.id, msg.guild.id);

    const needed = user.level * 100;
    const newXP = user.xp + xpGain;

    if (newXP >= needed) {
        db.prepare(`
        UPDATE users SET level = level + 1, xp = 0
        WHERE user_id = ? AND guild_id = ?
        `).run(msg.author.id, msg.guild.id);

        msg.channel.send(`🎉 ${msg.author} leveled up to **${user.level + 1}**!`);
    } else {
        db.prepare(`
        UPDATE users SET xp = ?
        WHERE user_id = ? AND guild_id = ?
        `).run(newXP, msg.author.id, msg.guild.id);
    }
});

/* AUTO BACKUPS (EVERY 6 HOURS) */
setInterval(() => {
    const src = '/data/poputil.db';
    const dest = `/data/backup-${Date.now()}.db`;

    fs.copyFileSync(src, dest);
    console.log('Database backup created:', dest);
}, 21600000);

/* Keep Render awake */
const app = express();
app.get('/', (_, res) => res.send('PopUtil running'));
app.listen(3000);

client.login(process.env.DISCORD_TOKEN);
