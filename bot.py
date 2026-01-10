import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import database

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class PopUtil(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")
        await self.tree.sync()

bot = PopUtil()

@bot.event
async def on_ready():
    print(f"PopUtil online as {bot.user}")

bot.run(TOKEN)
