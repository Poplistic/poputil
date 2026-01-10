import discord
from discord.ext import commands
from discord import app_commands
import os
import traceback
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class PopUtil(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")
                print(f"Loaded cog: {file}")

        await self.tree.sync()
        print("Slash commands synced.")

bot = PopUtil()

@bot.event
async def on_ready():
    print(f"PopUtil online as {bot.user}")

# -----------------------
# GLOBAL ERROR HANDLER
# -----------------------

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        return await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )

    if isinstance(error, app_commands.CommandOnCooldown):
        return await interaction.response.send_message(
            f"⏳ Try again in `{error.retry_after:.1f}` seconds.",
            ephemeral=True
        )

    traceback.print_exception(type(error), error, error.__traceback__)

    if not interaction.response.is_done():
        await interaction.response.send_message(
            "⚠️ An unexpected error occurred.",
            ephemeral=True
        )

bot.run(TOKEN)
