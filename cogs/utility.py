import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! `{latency}ms`")

    @app_commands.command(name="serverinfo", description="Get info about this server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(
            title=guild.name,
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Owner", value=guild.owner)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"))
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Get info about a user")
    @app_commands.describe(user="The user to look up")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member):
        embed = discord.Embed(
            title=str(user),
            color=user.color,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d"))
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d"))
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
