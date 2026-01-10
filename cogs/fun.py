import discord
from discord.ext import commands
from discord import app_commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        await interaction.response.send_message(random.choice(["🪙 Heads", "🪙 Tails"]))

    @app_commands.command(name="roll", description="Roll a dice")
    async def roll(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🎲 You rolled `{random.randint(1,6)}`")

async def setup(bot):
    await bot.add_cog(Fun(bot))
