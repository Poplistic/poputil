import discord
from discord.ext import commands
from discord import app_commands
import os

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reload", description="Reload a cog")
    async def reload(self, interaction: discord.Interaction, cog: str):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Admin only.", ephemeral=True)

        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"✅ Reloaded `{cog}`")
        except Exception as e:
            await interaction.response.send_message(str(e), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
