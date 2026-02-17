import discord
from discord import app_commands
from discord.ext import commands

class Noticias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="anunciar_jogo", description="Anuncia o próximo jogo do Glorioso manualmente")
    @app_commands.describe(
        adversario="Quem é o adversário?",
        data="Ex: 22/02",
        horario="Ex: 21:30",
        estadio="Ex: Nilton Santos",
        escudo_url="Link da imagem do escudo do adversário"
    )
    async def anunciar_jogo(self, interaction: discord.Interaction, adversario: str, data: str, horario: str, estadio: str, escudo_url: str):
        # ID do canal onde a notícia será postada
        CANAL_ID = 1461311054368739464
        canal = self.bot.get_channel(CANAL_ID)

        if not canal:
            await interaction.response.send_message("❌ Erro: Não encontrei o canal de notícias.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🔥 PRÓXIMO JOGO DO GLORIOSO",
            description=f"**Botafogo vs {adversario}**",
            color=0x000000
        )
        embed.add_field(name="📅 Data", value=data, inline=True)
        embed.add_field(name="🕒 Horário", value=horario, inline=True)
        embed.add_field(name="🏟️ Estádio", value=estadio, inline=False)
        embed.set_thumbnail(url=escudo_url)
        embed.set_author(name="Botafogo de Futebol e Regatas", icon_url="https://upload.wikimedia.org/wikipedia/commons/c/cb/Botafogo_de_Futebol_e_Regatas_logo.svg")
        embed.set_footer(text="Informativo Oficial Fogão Zone")

        await canal.send(content="📢 **O próximo jogo já está marcado!**", embed=embed)
        await interaction.response.send_message(f"✅ Jogo contra o {adversario} anunciado com sucesso!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Noticias(bot))