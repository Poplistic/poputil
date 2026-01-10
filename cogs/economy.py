import discord
from discord.ext import commands
from discord import app_commands
import database
import time
import random

# -----------------------
# CONSTANTS
# -----------------------

DAILY_AMOUNT = 250
WORK_COOLDOWN = 3600
CRIME_COOLDOWN = 7200
ROB_COOLDOWN = 3600

SHOP_ITEMS = {
    "cookie": {"price": 100, "description": "A tasty cookie 🍪"},
    "laptop": {"price": 2500, "description": "Used for work 💻"},
    "gun": {"price": 5000, "description": "Increases crime & rob success 🔫"}
}

# -----------------------
# ECONOMY COG
# -----------------------

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------
    # INTERNAL HELPERS
    # -----------------------

    def get_user(self, user_id, guild_id):
        database.cursor.execute(
            """
            SELECT balance, last_daily, last_work, last_crime
            FROM economy WHERE user_id=? AND guild_id=?
            """,
            (user_id, guild_id)
        )
        row = database.cursor.fetchone()

        if not row:
            database.cursor.execute(
                "INSERT INTO economy (user_id, guild_id) VALUES (?, ?)",
                (user_id, guild_id)
            )
            database.db.commit()
            return 0, 0, 0, 0

        return row

    def update_balance(self, user_id, guild_id, balance):
        database.cursor.execute(
            "UPDATE economy SET balance=? WHERE user_id=? AND guild_id=?",
            (balance, user_id, guild_id)
        )
        database.db.commit()

    def get_item(self, user_id, guild_id, item):
        database.cursor.execute(
            "SELECT amount FROM inventory WHERE user_id=? AND guild_id=? AND item=?",
            (user_id, guild_id, item)
        )
        row = database.cursor.fetchone()
        return row[0] if row else 0

    # -----------------------
    # BALANCE
    # -----------------------

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        bal, *_ = self.get_user(interaction.user.id, interaction.guild.id)
        await interaction.followup.send(f"💰 Balance: **{bal}** coins")

    # -----------------------
    # PAY
    # -----------------------

    @app_commands.command(name="pay", description="Pay another user")
    async def pay(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if user.bot or user == interaction.user:
            return await interaction.followup.send("❌ Invalid target.", ephemeral=True)

        if amount <= 0:
            return await interaction.followup.send("❌ Invalid amount.", ephemeral=True)

        bal, *_ = self.get_user(interaction.user.id, interaction.guild.id)
        if bal < amount:
            return await interaction.followup.send("❌ Not enough coins.", ephemeral=True)

        target_bal, *_ = self.get_user(user.id, interaction.guild.id)

        self.update_balance(interaction.user.id, interaction.guild.id, bal - amount)
        self.update_balance(user.id, interaction.guild.id, target_bal + amount)

        await interaction.followup.send(
            f"💸 {interaction.user.mention} paid {user.mention} **{amount}** coins"
        )

    # -----------------------
    # WORK
    # -----------------------

    @app_commands.command(name="work", description="Work to earn coins")
    async def work(self, interaction: discord.Interaction):
        bal, _, last_work, _ = self.get_user(interaction.user.id, interaction.guild.id)
        now = int(time.time())

        if now - last_work < WORK_COOLDOWN:
            remaining = WORK_COOLDOWN - (now - last_work)
            return await interaction.followup.send(
                f"⏳ Try again in **{remaining // 60} minutes**",
                ephemeral=True
            )

        earnings = 100
        if self.get_item(interaction.user.id, interaction.guild.id, "laptop"):
            earnings += 150

        database.cursor.execute(
            """
            UPDATE economy SET balance=?, last_work=?
            WHERE user_id=? AND guild_id=?
            """,
            (bal + earnings, now, interaction.user.id, interaction.guild.id)
        )
        database.db.commit()

        await interaction.followup.send(f"💼 You worked and earned **{earnings}** coins!")

    # -----------------------
    # CRIME
    # -----------------------

    @app_commands.command(name="crime", description="Commit a crime (high risk)")
    async def crime(self, interaction: discord.Interaction):
        bal, _, _, last_crime = self.get_user(interaction.user.id, interaction.guild.id)
        now = int(time.time())

        if now - last_crime < CRIME_COOLDOWN:
            remaining = CRIME_COOLDOWN - (now - last_crime)
            return await interaction.followup.send(
                f"⏳ Try again in **{remaining // 60} minutes**",
                ephemeral=True
            )

        success_chance = 0.4
        if self.get_item(interaction.user.id, interaction.guild.id, "gun"):
            success_chance += 0.2

        if random.random() < success_chance:
            reward = random.randint(300, 700)
            bal += reward
            message = f"🕵️ Crime successful! You gained **{reward}** coins."
        else:
            loss = random.randint(100, 300)
            bal = max(0, bal - loss)
            message = f"🚓 You got caught! You lost **{loss}** coins."

        database.cursor.execute(
            """
            UPDATE economy SET balance=?, last_crime=?
            WHERE user_id=? AND guild_id=?
            """,
            (bal, now, interaction.user.id, interaction.guild.id)
        )
        database.db.commit()

        await interaction.followup.send(message)

    # -----------------------
    # ROB (USER VS USER)
    # -----------------------

    @app_commands.command(name="rob", description="Rob another user (very risky)")
    async def rob(self, interaction: discord.Interaction, target: discord.Member):
        if target.bot or target == interaction.user:
            return await interaction.followup.send("❌ Invalid target.", ephemeral=True)

        robber_bal, *_ = self.get_user(interaction.user.id, interaction.guild.id)
        target_bal, *_ = self.get_user(target.id, interaction.guild.id)

        if target_bal < 100:
            return await interaction.followup.send(
                "❌ Target doesn't have enough coins to rob.",
                ephemeral=True
            )

        success_chance = 0.35
        if self.get_item(interaction.user.id, interaction.guild.id, "gun"):
            success_chance += 0.2

        if random.random() < success_chance:
            stolen = random.randint(100, min(500, target_bal))
            robber_bal += stolen
            target_bal -= stolen

            message = (
                f"🦹 **Robbery successful!**\n"
                f"You stole **{stolen}** coins from {target.mention}"
            )
        else:
            penalty = random.randint(100, min(300, robber_bal))
            robber_bal -= penalty

            message = (
                f"🚨 **Robbery failed!**\n"
                f"You were caught and lost **{penalty}** coins."
            )

        self.update_balance(interaction.user.id, interaction.guild.id, robber_bal)
        self.update_balance(target.id, interaction.guild.id, target_bal)

        await interaction.followup.send(message)

    # -----------------------
    # SHOP
    # -----------------------

    @app_commands.command(name="shop", description="View the shop")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛒 PopUtil Shop", color=discord.Color.green())

        for item, data in SHOP_ITEMS.items():
            embed.add_field(
                name=f"{item} — {data['price']} coins",
                value=data["description"],
                inline=False
            )

        await interaction.followup.send(embed=embed)

    # -----------------------
    # BUY
    # -----------------------

    @app_commands.command(name="buy", description="Buy an item")
    async def buy(self, interaction: discord.Interaction, item: str):
        item = item.lower()
        if item not in SHOP_ITEMS:
            return await interaction.followup.send("❌ Item not found.", ephemeral=True)

        bal, *_ = self.get_user(interaction.user.id, interaction.guild.id)
        price = SHOP_ITEMS[item]["price"]

        if bal < price:
            return await interaction.followup.send("❌ Not enough coins.", ephemeral=True)

        database.cursor.execute(
            "UPDATE economy SET balance=? WHERE user_id=? AND guild_id=?",
            (bal - price, interaction.user.id, interaction.guild.id)
        )
        database.cursor.execute(
            """
            INSERT INTO inventory (user_id, guild_id, item, amount)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(user_id, guild_id, item)
            DO UPDATE SET amount = amount + 1
            """,
            (interaction.user.id, interaction.guild.id, item)
        )
        database.db.commit()

        await interaction.followup.send(
            f"✅ You bought **{item}** for **{price}** coins"
        )

async def setup(bot):
    await bot.add_cog(Economy(bot))
