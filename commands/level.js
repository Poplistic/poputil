const { SlashCommandBuilder } = require('discord.js');
const db = require('../database/database');

module.exports = {
    data: new SlashCommandBuilder()
    .setName('level')
    .setDescription('Check your level and XP'),
    async execute(interaction) {
        const user = db.prepare(
            `SELECT xp, level FROM users WHERE user_id = ? AND guild_id = ?`
        ).get(interaction.user.id, interaction.guild.id);

        if (!user)
            return interaction.reply('📈 You have no XP yet.');

        const needed = user.level * 100;

        interaction.reply(
            `📈 **Level:** ${user.level}\n` +
            `⭐ **XP:** ${user.xp} / ${needed}`
        );
    }
};
