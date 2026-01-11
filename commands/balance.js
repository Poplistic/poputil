const { SlashCommandBuilder } = require('discord.js');
const db = require('../database/database');

module.exports = {
    data: new SlashCommandBuilder()
    .setName('balance')
    .setDescription('Check your coin balance'),
    async execute(interaction) {
        const user = db.prepare(
            `SELECT balance FROM users WHERE user_id = ? AND guild_id = ?`
        ).get(interaction.user.id, interaction.guild.id);

        const balance = user ? user.balance : 0;

        await interaction.reply(`💰 You have **${balance} coins**.`);
    }
};
