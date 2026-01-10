import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class PopUtil(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced.")

bot = PopUtil()

@bot.event
async def on_ready():
    print(f"PopUtil is online as {bot.user}")

# -----------------------
# BASIC UTILITIES
# -----------------------

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! `{latency}ms`")

@bot.tree.command(name="serverinfo", description="Get info about this server")
async def serverinfo(interaction: discord.Interaction):
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

@bot.tree.command(name="userinfo", description="Get info about a user")
@app_commands.describe(user="The user to look up")
async def userinfo(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(
        title=str(user),
        color=user.color,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d"))
    embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
    await interaction.response.send_message(embed=embed)

# -----------------------
# MODERATION
# -----------------------

@bot.tree.command(name="clear", description="Delete messages")
@app_commands.describe(amount="Number of messages to delete")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ No permission.", ephemeral=True)

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Deleted {amount} messages.", ephemeral=True)

@bot.tree.command(name="kick", description="Kick a member")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ No permission.", ephemeral=True)

    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member} was kicked.\nReason: {reason}")

@bot.tree.command(name="ban", description="Ban a member")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ No permission.", ephemeral=True)

    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {member} was banned.\nReason: {reason}")

bot.run(TOKEN)
