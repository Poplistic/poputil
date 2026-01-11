const { SlashCommandBuilder } = require('discord.js');
const db = require('../database/database');

module.exports = {
    data: new SlashCommandBuilder()
    .setName('leaderboard')
    .setDescription('Top 10 users by level'),
    async execute(interaction) {
        const rows = db.prepare(`
        SELECT user_id, level, xp
        FROM users
        WHERE guild_id = ?
        ORDER BY level DESC, xp DESC
        LIMIT 10
        `).all(interaction.guild.id);

        if (!rows.length)
            return interaction.reply('🏆 No leaderboard data yet.');

        const leaderboard = rows
        .map((u, i) =>
        `**${i + 1}.** <@${u.user_id}> — Level ${u.level} (${u.xp} XP)`
        )
        .join('\n');

        interaction.reply(`🏆 **Leaderboard**\n${leaderboard}`);
    }
};
