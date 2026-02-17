import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io


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
        # Pode deixar mais difícil depois se quiser
        return int((xp / 100) ** 0.5)

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
    # CRIAR IMAGEM DO PÓDIO
    # =============================

    async def create_podium(self, guild, ranking):

        width = 900
        height = 600

        image = Image.new("RGB", (width, height), (25, 25, 25))
        draw = ImageDraw.Draw(image)

        podium_heights = [300, 220, 180]

        positions = [
            (375, height - podium_heights[0]),  # 1º
            (150, height - podium_heights[1]),  # 2º
            (600, height - podium_heights[2])   # 3º
        ]

        colors = [
            (212, 175, 55),   # ouro
            (192, 192, 192),  # prata
            (205, 127, 50)    # bronze
        ]

        medals = ["🥇", "🥈", "🥉"]

        font_big = ImageFont.load_default()

        for i in range(min(3, len(ranking))):

            user_id, info = ranking[i]
            member = guild.get_member(int(user_id))
            if not member:
                continue

            x, y = positions[i]
            h = podium_heights[i]

            # Desenha base do pódio
            draw.rectangle([x, y, x+200, height], fill=colors[i])

            # Baixa avatar
            async with aiohttp.ClientSession() as session:
                async with session.get(member.display_avatar.url) as resp:
                    avatar_bytes = await resp.read()

            avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
            avatar = avatar.resize((140, 140))

            # Máscara redonda
            mask = Image.new("L", (140, 140), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 140, 140), fill=255)

            image.paste(avatar, (x+30, y-150), mask)

            # Medalha
            draw.text((x+85, y-190), medals[i], font=font_big, anchor="mm")

            # Nome
            draw.text((x+100, y+20), member.display_name[:10], fill="black", font=font_big, anchor="mm")

            # XP
            draw.text((x+100, y+50), f"{info['xp']} XP", fill="black", font=font_big, anchor="mm")

        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)

        return output

    # =============================
    # /rankserver
    # =============================

    @app_commands.command(name="rankserver", description="Veja o ranking do servidor")
    async def rankserver(self, interaction: discord.Interaction):

        await interaction.response.defer()

        data = self.load_data()
        ranking = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)

        if not ranking:
            await interaction.followup.send("Ainda não há ranking.")
            return

        podium_image = await self.create_podium(interaction.guild, ranking)

        file = discord.File(podium_image, filename="podium.png")

        await interaction.followup.send(file=file)


async def setup(bot):
    await bot.add_cog(XP(bot))
