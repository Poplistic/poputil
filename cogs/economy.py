import discord
from discord.ext import commands
from discord import app_commands
import database
import time
import random

# -----------------------
# CONSTANTS
# -----------------------

ECONOMY_CHANNEL_NAME = "economy"

WORK_COOLDOWN = 3600
CRIME_COOLDOWN = 7200
ROB_COOLDOWN = 3600

SHOP_ITEMS = {
    "cookie": {"price": 100, "description": "A tasty cookie 🍪"},
    "laptop": {"price": 2500, "description": "Boosts work income 💻"},
    "gun": {"price": 5000, "description": "Boosts crime & rob success 🔫"}
}

# -----------------------
# ECONOMY COG
# -----------------------

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------
    # CHANNEL CHECK
    # -----------------------

    async def economy_channel_only(self, interaction: discord.Interaction) -> bool:
        if interaction.channel.name != ECONOMY_CHANNEL_NAME:
            await interaction.followup.send(
                f"❌ Economy commands can only be used in **#{ECONOMY_CHANNEL_NAME}**.",
                ephemeral=True
            )
            return False
        return True

    # -----------------------
    # DATABASE HELPERS
    # -----------------------

    def get_user(self, user_id, guild_id):
        database.cursor.execute(
            """
            SELECT balance, last_work, last_crime
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
            return 0, 0, 0

        return row

    def set_balance(self, user_id, guild_id, balance):
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
        await interaction.response.defer()

        if not await self.economy_channel_only(interaction):
            return

        bal, _, _ = self.get_user(interaction.user.id, interaction.guild.id)
        await interaction.followup.send(f"💰 Balance: **{bal}** coins")

    # -----------------------
    # PAY
    # -----------------------

    @app_commands.command(name="pay", description="Pay another user")
    async def pay(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        await interaction.response.defer()

        if not await self.economy_channel_only(interaction):
            return

        if user.bot or user == interaction.user or amount <= 0:
            return await interaction.followup.send("❌ Invalid payment.", ephemeral=True)

        bal, _, _ = self.get_user(interaction.user.id, interaction.guild.id)
        target_bal, _, _ = self.get_user(user.id, interaction.guild.id)

        if bal < amount:
            return await interaction.followup.send("❌ Not enough coins.", ephemeral=True)

        self.set_balance(interaction.user.id, interaction.guild.id, bal - amount)
        self.set_balance(user.id, interaction.guild.id, target_bal + amount)

        await interaction.followup.send(
            f"💸 {interaction.user.mention} paid {user.mention} **{amount}** coins"
        )

    # -----------------------
    # WORK
    # -----------------------

    @app_commands.command(name="work", description="Work to earn coins")
    async def work(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if not await self.economy_channel_only(interaction):
            return

        bal, last_work, _ = self.get_user(interaction.user.id, interaction.guild.id)
        now = int(time.time())

        if now - last_work < WORK_COOLDOWN:
            mins = (WORK_COOLDOWN - (now - last_work)) // 60
            return await interaction.followup.send(
                f"⏳ Try again in **{mins} minutes**",
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

        await interaction.followup.send(f"💼 You earned **{earnings}** coins!")

    # -----------------------
    # CRIME
    # -----------------------

    @app_commands.command(name="crime", description="Commit a crime")
    async def crime(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if not await self.economy_channel_only(interaction):
            return

        bal, _, last_crime = self.get_user(interaction.user.id, interaction.guild.id)
        now = int(time.time())

        if now - last_crime < CRIME_COOLDOWN:
            mins = (CRIME_COOLDOWN - (now - last_crime)) // 60
            return await interaction.followup.send(
                f"⏳ Try again in **{mins} minutes**",
                ephemeral=True
            )

        chance = 0.4 + (0.2 if self.get_item(interaction.user.id, interaction.guild.id, "gun") else 0)

        if random.random() < chance:
            reward = random.randint(300, 700)
            bal += reward
            msg = f"🕵️ Success! You gained **{reward}** coins."
        else:
            loss = random.randint(100, min(300, bal))
            bal -= loss
            msg = f"🚓 Caught! You lost **{loss}** coins."

        database.cursor.execute(
            """
            UPDATE economy SET balance=?, last_crime=?
            WHERE user_id=? AND guild_id=?
            """,
            (bal, now, interaction.user.id, interaction.guild.id)
        )
        database.db.commit()

        await interaction.followup.send(msg)

    # -----------------------
    # ROB
    # -----------------------

    @app_commands.command(name="rob", description="Rob another user")
    async def rob(self, interaction: discord.Interaction, target: discord.Member):
        await interaction.response.defer()

        if not await self.economy_channel_only(interaction):
            return

        if target.bot or target == interaction.user:
            return await interaction.followup.send("❌ Invalid target.", ephemeral=True)

        bal, _, _ = self.get_user(interaction.user.id, interaction.guild.id)
        target_bal, _, _ = self.get_user(target.id, interaction.guild.id)

        if target_bal < 100:
            return await interaction.followup.send("❌ Target too poor to rob.", ephemeral=True)

        chance = 0.35 + (0.2 if self.get_item(interaction.user.id, interaction.guild.id, "gun") else 0)

        if random.random() < chance:
            stolen = random.randint(100, min(500, target_bal))
            bal += stolen
            target_bal -= stolen
            msg = f"🦹 You robbed **{stolen}** coins from {target.mention}"
        else:
            penalty = random.randint(100, min(300, bal))
            bal -= penalty
            msg = f"🚨 Robbery failed! You lost **{penalty}** coins."

        self.set_balance(interaction.user.id, interaction.guild.id, bal)
        self.set_balance(target.id, interaction.guild.id, target_bal)

        await interaction.followup.send(msg)

    # -----------------------
    # SHOP
    # -----------------------

    @app_commands.command(name="shop", description="View the shop")
    async def shop(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if not await self.economy_channel_only(interaction):
            return

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
        await interaction.response.defer()

        if not await self.economy_channel_only(interaction):
            return

        item = item.lower()
        if item not in SHOP_ITEMS:
            return await interaction.followup.send("❌ Item not found.", ephemeral=True)

        bal, _, _ = self.get_user(interaction.user.id, interaction.guild.id)
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
