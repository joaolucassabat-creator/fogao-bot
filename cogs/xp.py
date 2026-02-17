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

    # -----------------------------
    # Load / Save
    # -----------------------------
    def load_data(self):
        with open("xp.json", "r") as f:
            return json.load(f)

    def save_data(self, data):
        with open("xp.json", "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Calcula nível
    # -----------------------------
    def calculate_level(self, xp):
        return int(xp ** 0.5)

    # -----------------------------
    # Evento de mensagem
    # -----------------------------
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

    # -----------------------------
    # /rank
    # -----------------------------
    @app_commands.command(name="rank", description="Veja seu rank")
    async def rank(self, interaction):
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

    # -----------------------------
    # /rankserver (com podio)
    # -----------------------------
    @app_commands.command(name="rankserver", description="Veja o ranking do servidor")
    async def rankserver(self, interaction):
        await interaction.response.defer()

        data = self.load_data()
        ranking = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)

        if not ranking:
            await interaction.followup.send("Ainda não há ranking.")
            return

        podium_image = await self.create_podium(interaction.guild, ranking)
        file = discord.File(podium_image, filename="podium.png")
        await interaction.followup.send(file=file)

    # -----------------------------
    # Cria imagem do podio
    # -----------------------------
    async def create_podium(self, guild, ranking):
        width, height = 1000, 600
        podium_colors = [(192, 192, 192), (255, 215, 0), (205, 127, 50)]  # 2º, 1º, 3º
        podium_heights = [250, 350, 200]
        podium_positions = [(180, height - podium_heights[0]),
                            (420, height - podium_heights[1]),
                            (660, height - podium_heights[2])]

        # fundo gradiente
        image = Image.new("RGB", (width, height), (30, 30, 30))
        draw = ImageDraw.Draw(image)
        for i in range(height):
            gradient = int(30 + (i / height) * 70)
            draw.line([(0, i), (width, i)], fill=(gradient, gradient, gradient))

        # fonte
        try:
            font = ImageFont.truetype("Arial.ttf", 24)
            font_small = ImageFont.truetype("Arial.ttf", 20)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()

        async def get_avatar(member):
            async with aiohttp.ClientSession() as session:
                avatar_bytes = await member.avatar.read()
                avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
                avatar = avatar.resize((80, 80))
                # máscara circular
                mask = Image.new("L", (80, 80), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse((0, 0, 80, 80), fill=255)
                avatar.putalpha(mask)
                # moldura
                border = Image.new("RGBA", (84, 84), (255, 255, 255, 255))
                border.paste(avatar, (2, 2), avatar)
                return border

        # desenhar barras e avatares
        for i, pos in enumerate(podium_positions):
            x, y = pos
            # sombra 3D
            draw.rectangle([x + 5, y + 5, x + 105, height], fill=(0, 0, 0, 100))
            draw.rectangle([x, y, x + 100, height], fill=podium_colors[i])

            if i < len(ranking):
                user_id, info = ranking[i]
                member = guild.get_member(int(user_id))
                if member:
                    avatar = await get_avatar(member)
                    image.paste(avatar, (x + 10, y - 90), avatar)
                    draw.text((x + 10, y - 20), f"{member.display_name}",
                              fill="white", font=font, stroke_width=2, stroke_fill="black")
                    draw.text((x + 10, y + 10), f"Nível {info['level']}",
                              fill="white", font=font_small, stroke_width=2, stroke_fill="black")

        # top 10 lateral
        start_y = 50
        for i, (user_id, info) in enumerate(ranking[:10]):
            member = guild.get_member(int(user_id))
            if member:
                draw.text((850, start_y + i * 50),
                          f"{i+1}º - {member.display_name} | Nível {info['level']} ({info['xp']} XP)",
                          fill="white", font=font_small)

        # borda
        draw.rectangle([0, 0, width - 1, height - 1], outline=(255, 215, 0), width=4)

        # salvar em bytes
        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)
        return output


async def setup(bot):
    await bot.add_cog(XP(bot))
