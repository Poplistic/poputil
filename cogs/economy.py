import discord
from discord.ext import commands
from discord import app_commands
import database

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_balance(self, user, guild):
        cursor = database.cursor
        cursor.execute(
            "SELECT balance FROM economy WHERE user_id=? AND guild_id=?",
            (user.id, guild.id)
        )
        row = cursor.fetchone()
        if not row:
            cursor.execute(
                "INSERT INTO economy VALUES (?,?,?)",
                (user.id, guild.id, 0)
            )
            database.db.commit()
            return 0
        return row[0]

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        bal = self.get_balance(interaction.user, interaction.guild)
        await interaction.response.send_message(f"💰 Balance: `{bal}`")

async def setup(bot):
    await bot.add_cog(Economy(bot))
