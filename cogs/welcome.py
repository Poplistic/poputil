import discord
from discord.ext import commands
from discord import app_commands
import database

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setwelcome", description="Set welcome channel")
    async def setwelcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        database.cursor.execute(
            "INSERT OR REPLACE INTO config (guild_id, welcome_channel) VALUES (?,?)",
            (interaction.guild.id, channel.id)
        )
        database.db.commit()
        await interaction.response.send_message("✅ Welcome channel set")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        cursor = database.cursor
        cursor.execute("SELECT welcome_channel, autorole FROM config WHERE guild_id=?", (member.guild.id,))
        row = cursor.fetchone()
        if row:
            if row[0]:
                channel = member.guild.get_channel(row[0])
                await channel.send(f"👋 Welcome {member.mention}!")
            if row[1]:
                role = member.guild.get_role(row[1])
                await member.add_roles(role)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
