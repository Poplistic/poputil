import discord
from discord.ext import commands
from discord import app_commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reload", description="Reload a cog")
    @app_commands.checks.has_permissions(administrator=True)
    async def reload(self, interaction: discord.Interaction, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await interaction.followup.send(f"✅ Reloaded `{cog}`")
        except Exception as e:
            await interaction.followup.send(str(e), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
