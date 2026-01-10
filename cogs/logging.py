import discord
from discord.ext import commands
import database

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        cursor = database.cursor
        cursor.execute("SELECT log_channel FROM config WHERE guild_id=?", (member.guild.id,))
        row = cursor.fetchone()
        if row and row[0]:
            channel = member.guild.get_channel(row[0])
            await channel.send(f"📥 {member} joined the server")

async def setup(bot):
    await bot.add_cog(Logging(bot))
