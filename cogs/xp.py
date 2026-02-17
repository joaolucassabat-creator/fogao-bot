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
        """Retorna o nome do cargo baseado no XP atual"""
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

        # Ganho de XP: entre 15 e 35 para tornar a jornada desafiadora
        xp_gain = random.randint(15, 35)
        data[user_id]["xp"] += xp_gain
        
        # Verificar se subiu de nível/cargo
        current_xp = data[user_id]["xp"]
        rank_info = self.get_rank_info(current_xp)
        
        if rank_info["level"] > data[user_id]["level"]:
            data[user_id]["level"] = rank_info["level"]
            await self.update_member_roles(message.author, rank_info["id"])
            # Opcional: Enviar mensagem de parabenização
            # await message.channel.send(f"🔥 **GLORIOSO!** {message.author.mention} subiu para o nível **{rank_info['name']}**!")

        self.save_data(data)

    async def update_member_roles(self, member, new_role_id):
        """Dá o novo cargo e remove os outros cargos de nível que o bot gerencia"""
        new_role = member.guild.get_role(new_role_id)
        if not new_role:
            return

        # Lista de todos os IDs de cargos de nível para limpeza
        all_rank_ids = [r["id"] for r in self.rank_config]
        
        # Remove cargos antigos
        roles_to_remove = [member.guild.get_role(rid) for rid in all_rank_ids if rid != new_role_id]
        roles_to_remove = [r for r in roles_to_remove if r in member.roles]
        
        try:
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
            await member.add_roles(new_role)
        except Exception as e:
            print(f"Erro ao atualizar cargos: {e}")

    async def get_avatar_image(self, member, size=120):
        try:
            url = member.display_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    avatar_bytes = await response.read()
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
            avatar = avatar.resize((size, size), Image.Resampling.LANCZOS)
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            output.paste(avatar, (0, 0), mask)
            return output
        except:
            return Image.new("RGBA", (size, size), (50, 50, 50, 255))

@app_commands.command(name="rankserver", description="O Pódio Glorioso do Fogão")
async def rankserver(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = self.load_data()
        sorted_users = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)
        
        if not sorted_users:
            return await interaction.followup.send("Ranking vazio!")

        # 1. Configurar o Canvas (Tamanho maior para mais detalhe)
        width, height = 1000, 600
        # Criar um fundo com degradê estiloso (Preto para Cinza Chumbo)
        base = Image.new("RGBA", (width, height), (10, 10, 10, 255))
        draw = ImageDraw.Draw(base)

        # 2. Desenhar um brilho de fundo atrás do 1º lugar (Efeito de Holofote)
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        # Um círculo de luz branca bem suave no centro
        overlay_draw.ellipse((300, 50, 700, 450), fill=(255, 255, 255, 20)) 
        base = Image.alpha_composite(base, overlay)
        draw = ImageDraw.Draw(base)

        try:
            fnt_name = ImageFont.truetype("arialbd.ttf", 28) # Negrito
            fnt_xp = ImageFont.truetype("arial.ttf", 20)
            fnt_rank = ImageFont.truetype("arialbi.ttf", 40) # Itálico e Negrito
        except:
            fnt_name = fnt_xp = fnt_rank = ImageFont.load_default()

        # Configuração do Pódio Estilizado (FIFA Style)
        # (index, x, y_topo, largura, altura, cor_da_borda)
        podium_settings = [
            (1, 100, 280, 240, 320, (192, 192, 192, 150)), # 2º Prata
            (0, 380, 200, 240, 400, (255, 255, 255, 220)), # 1º Branco/Brilho
            (2, 660, 330, 240, 270, (205, 127, 50, 150))   # 3º Bronze
        ]

        for idx, x, y_top, w, h, b_color in podium_settings:
            if idx < len(sorted_users):
                u_id, u_data = sorted_users[idx]
                member = interaction.guild.get_member(int(u_id))
                
                # Criar o Card (Retângulo arredondado com transparência)
                card_shape = [x, y_top, x + w, height - 20]
                # Preenchimento do card (Efeito de vidro escuro)
                draw.rounded_rectangle(card_shape, radius=20, fill=(30, 30, 30, 180), outline=b_color, width=3)

                # Foto do Jogador (Maior e com borda)
                if member:
                    avatar = await self.get_avatar_image(member, size=150)
                    # Centralizar avatar no card
                    base.paste(avatar, (x + (w//2 - 75), y_top - 80), avatar)
                    
                    # Nome do "Craque"
                    name = member.display_name[:12].upper()
                    draw.text((x + 20, y_top + 80), name, fill="white", font=fnt_name)
                    
                    # Info do Cargo
                    rank_info = self.get_rank_info(u_data['xp'])
                    draw.text((x + 20, y_top + 115), f"LVL {u_data['level']} • {rank_info['name']}", fill=b_color, font=fnt_xp)
                    
                    # XP total
                    draw.text((x + 20, y_top + 145), f"XP: {u_data['xp']:,}", fill=(200, 200, 200), font=fnt_xp)

                # Número da posição gigante e estilizado no fundo do card
                draw.text((x + w - 70, y_top + h - 130), f"{idx+1}", fill=(255, 255, 255, 30), font=fnt_rank)

        # Adicionar uma Estrela Solitária simbólica no canto (Usando caracteres ou desenho)
        draw.text((width - 80, 20), "★", fill="white", font=fnt_rank)

        # Enviar imagem finalizada
        with io.BytesIO() as binary_img:
            base.save(binary_img, "PNG")
            binary_img.seek(0)
            await interaction.followup.send(file=discord.File(binary_img, "podium_pro.png"))


async def setup(bot):
    await bot.add_cog(XP(bot))