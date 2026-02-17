import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random


class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists("xp.json"):
            with open("xp.json", "w") as f:
                json.dump({}, f)

    def load_data(self):
        with open("xp.json", "r") as f:
            return json.load(f)

    def save_data(self, data):
        with open("xp.json", "w") as f:
            json.dump(data, f, indent=4)

    def calculate_level(self, xp):
        return int(xp ** 0.5)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        data = self.load_data()
        user_id = str(message.author.id)

        if user_id not in data:
            data[user_id] = {"xp": 0, "level": 0}

        data[user_id]["xp"] += random.randint(5, 15)
        data[user_id]["level"] = self.calculate_level(data[user_id]["xp"])

        self.save_data(data)

    # =============================
    # /rank
    # =============================

    @app_commands.command(name="rank", description="Veja seu rank")
    async def rank(self, interaction: discord.Interaction):

        data = self.load_data()
        user_id = str(interaction.user.id)

        if user_id not in data:
            await interaction.response.send_message("Você ainda não tem XP.")
            return

        xp = data[user_id]["xp"]
        level = data[user_id]["level"]

        embed = discord.Embed(
            title=f"Rank de {interaction.user.display_name}",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Nível", value=level)
        embed.add_field(name="XP", value=xp)

        await interaction.response.send_message(embed=embed)

    # =============================
    # /rankserver
    # =============================

    @app_commands.command(name="rankserver", description="Veja o ranking do servidor")
    async def rankserver(self, interaction):

        await interaction.response.defer()

        data = self.load_data()

        ranking = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)

        embed = discord.Embed(
            title="🏆 Ranking do Servidor",
            color=discord.Color.dark_grey()
        )

        description = ""

        for i, (user_id, info) in enumerate(ranking[:10], start=1):
            member = interaction.guild.get_member(int(user_id))
            if member:
                description += f"**{i}º** - {member.mention} | Nível {info['level']} ({info['xp']} XP)\n"

        embed.description = description

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(XP(bot))
