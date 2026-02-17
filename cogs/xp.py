import discord
from discord.ext import commands
from discord import app_commands, Interaction
import json
import os
import random
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configuração Oficial: XP Necessário e ID do Cargo
        self.rank_config = [
            {"level": 1, "xp_needed": 500, "id": 1461307537725853696, "name": "Novato"},
            {"level": 2, "xp_needed": 1500, "id": 1461307812612276405, "name": "Aspirante"},
            {"level": 3, "xp_needed": 5000, "id": 1461308013968101428, "name": "Aprendiz"},
            {"level": 4, "xp_needed": 15000, "id": 1461308193065013258, "name": "Técnico"},
            {"level": 5, "xp_needed": 50000, "id": 1461308733111144489, "name": "Jogador"},
            {"level": 6, "xp_needed": 100000, "id": 1461309027832037476, "name": "Craque"},
            {"level": 7, "xp_needed": 200000, "id": 1461309179800059971, "name": "Veterano"},
            {"level": 8, "xp_needed": 350000, "id": 1461309381348950199, "name": "Ídolo"},
            {"level": 9, "xp_needed": 500000, "id": 1461309629140308104, "name": "Capitão"},
            {"level": 10, "xp_needed": 750000, "id": 1461309970715902015, "name": "Lenda"},
            {"level": 11, "xp_needed": 1000000, "id": 1461310182041845815, "name": "Estrela"},
            {"level": 12, "xp_needed": 1300000, "id": 1461310395213156407, "name": "Perito"},
            {"level": 13, "xp_needed": 1500000, "id": 1461310572065849415, "name": "Tático"},
            {"level": 14, "xp_needed": 1750000, "id": 1461310873837633761, "name": "Ícone"},
            {"level": 15, "xp_needed": 2000000, "id": 1461311054368739464, "name": "Imortal"},
        ]
        
        if not os.path.exists("xp.json"):
            with open("xp.json", "w") as f:
                json.dump({}, f)

    def load_data(self):
        with open("xp.json", "r") as f:
            return json.load(f)

    def save_data(self, data):
        with open("xp.json", "w") as f:
            json.dump(data, f, indent=4)

    def get_rank_info(self, xp):
        current_rank = {"name": "Membro", "level": 0}
        for rank in self.rank_config:
            if xp >= rank["xp_needed"]:
                current_rank = rank
            else:
                break
        return current_rank

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        data = self.load_data()
        user_id = str(message.author.id)

        if user_id not in data:
            data[user_id] = {"xp": 0, "level": 0}

        data[user_id]["xp"] += random.randint(15, 35)
        current_xp = data[user_id]["xp"]
        rank_info = self.get_rank_info(current_xp)
        
        if rank_info["level"] > data[user_id].get("level", 0):
            data[user_id]["level"] = rank_info["level"]
            await self.update_member_roles(message.author, rank_info["id"])

        self.save_data(data)

    async def update_member_roles(self, member, new_role_id):
        new_role = member.guild.get_role(new_role_id)
        if not new_role: return
        all_rank_ids = [r["id"] for r in self.rank_config]
        roles_to_remove = [member.guild.get_role(rid) for rid in all_rank_ids if rid != new_role_id]
        roles_to_remove = [r for r in roles_to_remove if r and r in member.roles]
        try:
            if roles_to_remove: await member.remove_roles(*roles_to_remove)
            await member.add_roles(new_role)
        except: pass

    async def get_avatar_image(self, member, size=150):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(member.display_avatar.url)) as resp:
                    if resp.status == 200:
                        avatar_bytes = await resp.read()
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
            avatar = avatar.resize((size, size), Image.LANCZOS)
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            output.paste(avatar, (0, 0), mask)
            return output
        except:
            return Image.new("RGBA", (size, size), (40, 40, 40, 255))

    @app_commands.command(name="rankserver", description="O Pódio Glorioso do Fogão")
    async def rankserver(self, interaction: Interaction):
        await interaction.response.defer()
        data = self.load_data()
        sorted_users = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)
        if not sorted_users:
            return await interaction.followup.send("Ranking vazio!")

        width, height = 1000, 600
        base = Image.new("RGBA", (width, height), (5, 5, 5, 255))
        draw = ImageDraw.Draw(base)

        # Holofote central
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(overlay).ellipse((300, 50, 700, 450), fill=(255, 255, 255, 15)) 
        base = Image.alpha_composite(base, overlay)
        draw = ImageDraw.Draw(base)

        try:
            fnt_name = ImageFont.truetype("arial.ttf", 28)
            fnt_xp = ImageFont.truetype("arial.ttf", 20)
            fnt_rank = ImageFont.truetype("arial.ttf", 40)
        except:
            fnt_name = fnt_xp = fnt_rank = ImageFont.load_default()

        # (index, x, y_top, w, h, border_color)
        podium_settings = [
            (1, 80, 280, 260, 300, (192, 192, 192, 180)), # 2º Prata
            (0, 370, 200, 260, 380, (255, 255, 255, 255)), # 1º Branco
            (2, 660, 330, 260, 250, (205, 127, 50, 180))   # 3º Bronze
        ]

        for idx, x, y_top, w, h, b_color in podium_settings:
            if idx < len(sorted_users):
                u_id, u_data = sorted_users[idx]
                member = interaction.guild.get_member(int(u_id))
                
                # Card Estilo FIFA
                draw.rounded_rectangle([x, y_top, x + w, height - 20], radius=15, fill=(25, 25, 25, 200), outline=b_color, width=2)

                if member:
                    avatar = await self.get_avatar_image(member, size=140)
                    base.paste(avatar, (x + (w//2 - 70), y_top - 75), avatar)
                    draw.text((x + 20, y_top + 80), member.display_name[:14].upper(), fill="white", font=fnt_name)
                    
                    r_info = self.get_rank_info(u_data['xp'])
                    draw.text((x + 20, y_top + 115), f"LVL {u_data['level']} • {r_info['name']}", fill=b_color, font=fnt_xp)
                    draw.text((x + 20, y_top + 140), f"XP: {u_data['xp']:,}", fill=(180, 180, 180), font=fnt_xp)

                draw.text((x + w - 60, y_top + h - 110), f"{idx+1}", fill=(255, 255, 255, 20), font=fnt_rank)

        draw.text((width - 60, 20), "★", fill="white", font=fnt_rank)

        with io.BytesIO() as binary_img:
            base.save(binary_img, "PNG")
            binary_img.seek(0)
            await interaction.followup.send(file=discord.File(binary_img, "podium_pro.png"))

# FORA DA CLASSE - ENCOSTADO NA PAREDE ESQUERDA
async def setup(bot: commands.Bot):
    await bot.add_cog(XP(bot))