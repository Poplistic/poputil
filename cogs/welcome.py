import discord
from discord.ext import commands
from discord import app_commands
import database

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------
    # SET WELCOME CHANNEL
    # -----------------------

    @app_commands.command(name="setwelcome", description="Set the welcome channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setwelcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        database.cursor.execute(
            """
            INSERT INTO config (guild_id, welcome_channel)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET welcome_channel=excluded.welcome_channel
            """,
            (interaction.guild.id, channel.id)
        )
        database.db.commit()

        await interaction.followup.send(
            f"✅ Welcome channel set to {channel.mention}",
            ephemeral=True
        )

    # -----------------------
    # SET AUTOROLE
    # -----------------------

    @app_commands.command(name="setautorole", description="Set the autorole for new members")
    @app_commands.checks.has_permissions(administrator=True)
    async def setautorole(self, interaction: discord.Interaction, role: discord.Role):
        database.cursor.execute(
            """
            INSERT INTO config (guild_id, autorole)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET autorole=excluded.autorole
            """,
            (interaction.guild.id, role.id)
        )
        database.db.commit()

        await interaction.followup.send(
            f"✅ Autorole set to {role.mention}",
            ephemeral=True
        )

    # -----------------------
    # MEMBER JOIN EVENT
    # -----------------------

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        database.cursor.execute(
            "SELECT welcome_channel, autorole FROM config WHERE guild_id=?",
            (member.guild.id,)
        )
        row = database.cursor.fetchone()

        if not row:
            return

        welcome_channel_id, autorole_id = row

        # Welcome message
        if welcome_channel_id:
            channel = member.guild.get_channel(welcome_channel_id)
            if channel:
                await channel.send(f"👋 Welcome {member.mention} to **{member.guild.name}**!")

        # Autorole
        if autorole_id:
            role = member.guild.get_role(autorole_id)
            if role:
                try:
                    await member.add_roles(role, reason="PopUtil autorole")
                except discord.Forbidden:
                    pass

async def setup(bot):
    await bot.add_cog(Welcome(bot))
