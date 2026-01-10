import discord
from discord.ext import commands
from discord import app_commands
import database
import time

DAILY_AMOUNT = 250
DAILY_COOLDOWN = 86400  # 24 hours

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------
    # INTERNAL HELPERS
    # -----------------------

    def get_user(self, user_id: int, guild_id: int):
        database.cursor.execute(
            "SELECT balance, last_daily FROM economy WHERE user_id=? AND guild_id=?",
            (user_id, guild_id)
        )
        row = database.cursor.fetchone()

        if not row:
            database.cursor.execute(
                "INSERT INTO economy (user_id, guild_id) VALUES (?, ?)",
                (user_id, guild_id)
            )
            database.db.commit()
            return 0, 0

        return row

    # -----------------------
    # BALANCE
    # -----------------------

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        balance, _ = self.get_user(interaction.user.id, interaction.guild.id)
        await interaction.followup.send(f"💰 Your balance: **{balance}** coins")

    # -----------------------
    # DAILY
    # -----------------------

    @app_commands.command(name="daily", description="Claim your daily coins")
    async def daily(self, interaction: discord.Interaction):
        balance, last_daily = self.get_user(interaction.user.id, interaction.guild.id)
        now = int(time.time())

        if now - last_daily < DAILY_COOLDOWN:
            remaining = DAILY_COOLDOWN - (now - last_daily)
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            return await interaction.followup.send(
                f"⏳ You can claim again in **{hours}h {minutes}m**",
                ephemeral=True
            )

        new_balance = balance + DAILY_AMOUNT

        database.cursor.execute(
            """
            UPDATE economy
            SET balance=?, last_daily=?
            WHERE user_id=? AND guild_id=?
            """,
            (new_balance, now, interaction.user.id, interaction.guild.id)
        )
        database.db.commit()

        await interaction.followup.send(
            f"🎁 You claimed **{DAILY_AMOUNT}** coins!\n💰 New balance: **{new_balance}**"
        )

    # -----------------------
    # GIVE (ADMIN)
    # -----------------------

    @app_commands.command(name="give", description="Give coins to a user")
    @app_commands.checks.has_permissions(administrator=True)
    async def give(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if amount <= 0:
            return await interaction.followup.send("❌ Amount must be positive.", ephemeral=True)

        balance, last_daily = self.get_user(user.id, interaction.guild.id)
        new_balance = balance + amount

        database.cursor.execute(
            """
            UPDATE economy
            SET balance=?
            WHERE user_id=? AND guild_id=?
            """,
            (new_balance, user.id, interaction.guild.id)
        )
        database.db.commit()

        await interaction.followup.send(
            f"✅ Gave **{amount}** coins to {user.mention}\n💰 New balance: **{new_balance}**"
        )

    # -----------------------
    # LEADERBOARD
    # -----------------------

    @app_commands.command(name="leaderboard", description="Top 10 richest users")
    async def leaderboard(self, interaction: discord.Interaction):
        database.cursor.execute(
            """
            SELECT user_id, balance
            FROM economy
            WHERE guild_id=?
            ORDER BY balance DESC
            LIMIT 10
            """,
            (interaction.guild.id,)
        )
        rows = database.cursor.fetchall()

        if not rows:
            return await interaction.followup.send("No data yet.")

        embed = discord.Embed(
            title="🏆 Economy Leaderboard",
            color=discord.Color.gold()
        )

        for i, (user_id, balance) in enumerate(rows, start=1):
            user = interaction.guild.get_member(user_id)
            name = user.display_name if user else f"User {user_id}"
            embed.add_field(
                name=f"{i}. {name}",
                value=f"💰 {balance} coins",
                inline=False
            )

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
