const { SlashCommandBuilder } = require('discord.js');
const db = require('../database/database');

module.exports = {
    data: new SlashCommandBuilder()
    .setName('buy')
    .setDescription('Buy an item')
    .addStringOption(o =>
    o.setName('item').setRequired(true)),
    async execute(i) {
        const itemName = i.options.getString('item');

        const item = db.prepare(
            `SELECT * FROM shop WHERE item = ?`
        ).get(itemName);

        if (!item) return i.reply('❌ Item not found.');

        const user = db.prepare(
            `SELECT * FROM users WHERE user_id = ? AND guild_id = ?`
        ).get(i.user.id, i.guild.id);

        if (!user || user.balance < item.price)
            return i.reply('❌ Not enough coins.');

        db.prepare(`
        UPDATE users SET balance = balance - ?
        WHERE user_id = ? AND guild_id = ?
        `).run(item.price, i.user.id, i.guild.id);

        db.prepare(`
        INSERT INTO inventory (user_id, guild_id, item, amount)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(user_id, guild_id, item)
        DO UPDATE SET amount = amount + 1
        `).run(i.user.id, i.guild.id, itemName);

        i.reply(`✅ Purchased **${itemName}**!`);
    }
};
