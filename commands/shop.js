const { SlashCommandBuilder } = require('discord.js');
const db = require('../database/database');

module.exports = {
    data: new SlashCommandBuilder()
    .setName('shop')
    .setDescription('View shop items'),
    async execute(i) {
        const items = db.prepare(`SELECT * FROM shop`).all();
        const text = items.map(x =>
        `🛒 **${x.item}** — ${x.price} coins`
        ).join('\n');
        i.reply(text);
    }
};
