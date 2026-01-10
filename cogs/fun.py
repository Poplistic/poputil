import discord
from discord.ext import commands
from discord import app_commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            random.choice(["🪙 Heads", "🪙 Tails"])
        )

    @app_commands.command(name="roll", description="Roll a dice")
    async def roll(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"🎲 You rolled `{random.randint(1, 6)}`"
        )

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = [
            "🎱 Yes",
            "🎱 No",
            "🎱 Maybe",
            "🎱 Definitely",
            "🎱 Absolutely not",
            "🎱 Ask again later",
            "🎱 It is certain",
            "🎱 Very doubtful"
        ]
        await interaction.response.send_message(
            f"**Question:** {question}\n**Answer:** {random.choice(responses)}"
        )

    @app_commands.command(name="rps", description="Play Rock, Paper, Scissors")
    @app_commands.choices(
        choice=[
            app_commands.Choice(name="Rock", value="rock"),
            app_commands.Choice(name="Paper", value="paper"),
            app_commands.Choice(name="Scissors", value="scissors"),
        ]
    )
    async def rps(self, interaction: discord.Interaction, choice: app_commands.Choice[str]):
        bot_choice = random.choice(["rock", "paper", "scissors"])

        if choice.value == bot_choice:
            result = "It's a tie!"
        elif (
            (choice.value == "rock" and bot_choice == "scissors") or
            (choice.value == "paper" and bot_choice == "rock") or
            (choice.value == "scissors" and bot_choice == "paper")
        ):
            result = "You win! 🎉"
        else:
            result = "You lose! 😢"

        await interaction.response.send_message(
            f"🧠 You chose **{choice.value}**\n"
            f"🤖 I chose **{bot_choice}**\n\n"
            f"**{result}**"
        )

    @app_commands.command(name="choose", description="Let the bot choose for you")
    async def choose(self, interaction: discord.Interaction, options: str):
        choices = [opt.strip() for opt in options.split(",") if opt.strip()]
        if len(choices) < 2:
            await interaction.response.send_message(
                "❌ Please provide at least two options separated by commas."
            )
            return

        await interaction.response.send_message(
            f"🤔 I choose: **{random.choice(choices)}**"
        )

    @app_commands.command(name="rate", description="Rate something from 1 to 10")
    async def rate(self, interaction: discord.Interaction, thing: str):
        await interaction.response.send_message(
            f"⭐ I rate **{thing}** a **{random.randint(1, 10)}/10**"
        )

async def setup(bot):
    await bot.add_cog(Fun(bot))
