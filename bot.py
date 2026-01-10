import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

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
        # Load all cogs
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")
                print(f"Loaded cog: {file}")

        # Sync slash commands
        await self.tree.sync()
        print("Slash commands synced.")

bot = PopUtil()

@bot.event
async def on_ready():
    print(f"PopUtil is online as {bot.user}")

bot.run(TOKEN)
