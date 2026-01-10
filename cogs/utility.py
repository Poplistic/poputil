import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    @app_commands.checks.cooldown(1, 5)
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.followup.send(f"🏓 Pong! `{latency}ms`")

    @app_commands.command(name="userinfo", description="Get info about a user")
    @app_commands.describe(user="The user to look up")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member):
        embed = discord.Embed(
            title=str(user),
            color=user.color if user.color.value else discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="Joined Server",
            value=user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Unknown",
            inline=False
        )

        embed.add_field(
            name="Account Created",
            value=user.created_at.strftime("%Y-%m-%d"),
            inline=False
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
