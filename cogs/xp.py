import discord
from discord.ext import commands
import json
import os
import random

LEVEL_ROLES = {
    15: 1461311054368739464,
    14: 1461310873837633761,
    13: 1461310572065849415,
    12: 1461310395213156407,
    11: 1461310182041845815,
    10: 1461309970715902015,
    9: 1461309629140308104,
    8: 1461309381348950199,
    7: 1461309179800059971,
    6: 1461309027832037476,
    5: 1461308733111144489,
    4: 1461308193065013258,
    3: 1461308013968101428,
    2: 1461307812612276405,
    1: 1461307537725853696
}


def calculate_level(xp):
    level = 0
    while xp >= (100 * (level + 1)):
        level += 1
    return level



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

    async def update_roles(self, member, level):
        guild = member.guild

        for role_id in LEVEL_ROLES.values():
            role = guild.get_role(role_id)
            if role in member.roles:
                await member.remove_roles(role)

        for lvl in sorted(LEVEL_ROLES.keys(), reverse=True):
            if level >= lvl:
                role = guild.get_role(LEVEL_ROLES[lvl])
                await member.add_roles(role)
                break

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        data = self.load_data()
        user_id = str(message.author.id)

        if user_id not in data:
            data[user_id] = {"xp": 0, "level": 0}

        old_level = data[user_id]["level"]

        xp_gain = random.randint(5, 15)
        data[user_id]["xp"] += xp_gain

        new_level = calculate_level(data[user_id]["xp"])
        data[user_id]["level"] = new_level

        self.save_data(data)

        if new_level > old_level:
            await self.update_roles(message.author, new_level)

            embed = discord.Embed(
                title="⚫⚪ SUBIU DE NÍVEL! ⚪⚫",
                description=f"{message.author.mention} agora é **Nível {new_level}**!\n\n🔥 O FOGÃO TÁ VOANDO! 🔥",
                color=discord.Color.dark_grey()
            )

            await message.channel.send(embed=embed)

    @discord.app_commands.command(name="rank", description="Veja seu rank")
    async def rank(self, interaction: discord.Interaction):
        await interaction.response.defer()

        data = self.load_data()
        user_id = str(interaction.user.id)

        if user_id not in data:
            await interaction.followup.send("Você ainda não tem XP.")
            return

        xp = data[user_id]["xp"]
        level = data[user_id]["level"]

        embed = discord.Embed(
            title=f"⚫⚪ Rank de {interaction.user.display_name} ⚪⚫",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Nível", value=level)
        embed.add_field(name="XP", value=xp)

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(XP(bot))

