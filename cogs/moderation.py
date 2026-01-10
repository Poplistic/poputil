import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Delete messages")
    @app_commands.describe(amount="Number of messages to delete")
    async def clear(self, interaction: discord.Interaction, amount: int):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message(
                "❌ You don't have permission.",
                ephemeral=True
            )

        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(
            f"🧹 Deleted {amount} messages.",
            ephemeral=True
        )

    @app_commands.command(name="kick", description="Kick a member")
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        if not interaction.user.guild_permissions.kick_members:
            return await interaction.response.send_message(
                "❌ You don't have permission.",
                ephemeral=True
            )

        await member.kick(reason=reason)
        await interaction.response.send_message(
            f"👢 {member} was kicked.\nReason: {reason}"
        )

    @app_commands.command(name="ban", description="Ban a member")
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        if not interaction.user.guild_permissions.ban_members:
            return await interaction.response.send_message(
                "❌ You don't have permission.",
                ephemeral=True
            )

        await member.ban(reason=reason)
        await interaction.response.send_message(
            f"🔨 {member} was banned.\nReason: {reason}"
        )

async def setup(bot):
    await bot.add_cog(Moderation(bot))
