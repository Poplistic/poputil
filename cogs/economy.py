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

SHOP_ITEMS = {
    "cookie": {"price": 100, "description": "A tasty cookie 🍪"},
    "laptop": {"price": 2500, "description": "Used for work 💻"},
    "gun": {"price": 5000, "description": "Increases crime success 🔫"}
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
            "SELECT balance, last_daily, last_work, last_crime FROM economy WHERE user_id=? AND guild_id=?",
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

    def add_balance(self, user_id, guild_id, amount):
        bal, d, w, c = self.get_user(user_id, guild_id)
        database.cursor.execute(
            "UPDATE economy SET balance=? WHERE user_id=? AND guild_id=?",
            (bal + amount, user_id, guild_id)
        )
        database.db.commit()

    def get_item(self, user_id, guild_id, item):
        database.cursor.execute(
            "SELECT amount FROM inventory WHERE user_id=? AND guild_id=? AND item=?",
            (user_id, guild_id, item)
        )
        row = database.cursor.fetchone()
        return row[0] if row else 0

    def add_item(self, user_id, guild_id, item, amount):
        current = self.get_item(user_id, guild_id, item)
        if current == 0:
            database.cursor.execute(
                "INSERT INTO inventory VALUES (?, ?, ?, ?)",
                (user_id, guild_id, item, amount)
            )
        else:
            database.cursor.execute(
                "UPDATE inventory SET amount=? WHERE user_id=? AND guild_id=? AND item=?",
                (current + amount, user_id, guild_id, item)
            )
        database.db.commit()

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
        if amount <= 0:
            return await interaction.followup.send("❌ Invalid amount.", ephemeral=True)

        bal, *_ = self.get_user(interaction.user.id, interaction.guild.id)
        if bal < amount:
            return await interaction.followup.send("❌ Not enough coins.", ephemeral=True)

        self.add_balance(interaction.user.id, interaction.guild.id, -amount)
        self.add_balance(user.id, interaction.guild.id, amount)

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

        bonus = 100
        if self.get_item(interaction.user.id, interaction.guild.id, "laptop"):
            bonus += 150

        database.cursor.execute(
            "UPDATE economy SET balance=?, last_work=? WHERE user_id=? AND guild_id=?",
            (bal + bonus, now, interaction.user.id, interaction.guild.id)
        )
        database.db.commit()

        await interaction.followup.send(f"💼 You worked and earned **{bonus}** coins!")

    # -----------------------
    # CRIME
    # -----------------------

    @app_commands.command(name="crime", description="Commit a crime (risk!)")
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
            fine = random.randint(100, 300)
            bal = max(0, bal - fine)
            message = f"🚓 You got caught! You lost **{fine}** coins."

        database.cursor.execute(
            "UPDATE economy SET balance=?, last_crime=? WHERE user_id=? AND guild_id=?",
            (bal, now, interaction.user.id, interaction.guild.id)
        )
        database.db.commit()

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

        self.add_balance(interaction.user.id, interaction.guild.id, -price)
        self.add_item(interaction.user.id, interaction.guild.id, item, 1)

        await interaction.followup.send(
            f"✅ You bought **{item}** for **{price}** coins"
        )

async def setup(bot):
    await bot.add_cog(Economy(bot))
