const { SlashCommandBuilder } = require('discord.js');
const db = require('../database/database');

module.exports = {
    data: new SlashCommandBuilder()
    .setName('inventory')
    .setDescription('View your inventory'),
    async execute(i) {
        const items = db.prepare(`
        SELECT * FROM inventory
        WHERE user_id = ? AND guild_id = ?
        `).all(i.user.id, i.guild.id);

        if (!items.length)
            return i.reply('📦 Inventory empty.');

        const text = items.map(x =>
        `• ${x.item} x${x.amount}`
        ).join('\n');

        i.reply(`📦 **Inventory**\n${text}`);
    }
};
