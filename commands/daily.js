const { SlashCommandBuilder } = require('discord.js');
const db = require('../database/database');

const DAILY_AMOUNT = 100;
const COOLDOWN = 86400000; // 24 hours

module.exports = {
    data: new SlashCommandBuilder()
    .setName('daily')
    .setDescription('Claim your daily coins'),
    async execute(interaction) {
        const now = Date.now();

        let user = db.prepare(
            `SELECT * FROM users WHERE user_id = ? AND guild_id = ?`
        ).get(interaction.user.id, interaction.guild.id);

        if (!user) {
            db.prepare(`
            INSERT INTO users (user_id, guild_id, balance, last_daily)
            VALUES (?, ?, ?, ?)
            `).run(interaction.user.id, interaction.guild.id, DAILY_AMOUNT, now);

            return interaction.reply(`💰 You claimed **${DAILY_AMOUNT} coins**!`);
        }

        if (now - user.last_daily < COOLDOWN) {
            const remaining = COOLDOWN - (now - user.last_daily);
            const hours = Math.ceil(remaining / 3600000);
            return interaction.reply(`⏳ You can claim again in **${hours}h**.`);
        }

        db.prepare(`
        UPDATE users
        SET balance = balance + ?, last_daily = ?
        WHERE user_id = ? AND guild_id = ?
        `).run(DAILY_AMOUNT, now, interaction.user.id, interaction.guild.id);

        interaction.reply(`💰 You claimed **${DAILY_AMOUNT} coins**!`);
    }
};
