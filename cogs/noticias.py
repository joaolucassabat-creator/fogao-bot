import discord
from discord.ext import commands, tasks
import aiohttp
import os
from datetime import datetime

class Noticias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verificar_jogos.start() # Inicia o loop automático

    def cog_unload(self):
        self.verificar_jogos.cancel() # Para o loop se o bot desligar

    @tasks.loop(hours=24)
    async def verificar_jogos(self):
        # --- CONFIGURAÇÕES ---
        CANAL_ID = 1461344345289654292  # <--- COLOQUE O ID DO SEU CANAL AQUI!
        BOTAFOGO_ID = 120
        API_KEY = os.getenv("FOOTBALL_API_KEY")
        
        if not API_KEY:
            print("ERRO: FOOTBALL_API_KEY não encontrada nas variáveis de ambiente.")
            return

        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        
        # Consulta o próximo jogo do Botafogo
        url = f"https://v3.football.api-sports.io/fixtures?team={BOTAFOGO_ID}&next=1"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('response'):
                            jogo = data['response'][0]
                            # Formata a data (Ex: 2026-02-17T21:30:00+00:00)
                            data_str = jogo['fixture']['date']
                            data_jogo = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
                            
                            # Verifica se o jogo é HOJE (comparando data atual)
                            hoje = datetime.now().date()
                            if True: # Isso força o bot a ignorar a data e postar o próximo jogo encontrado
                                canal = self.bot.get_channel(CANAL_ID)
                                if canal:
                                    home = jogo['teams']['home']['name']
                                    away = jogo['teams']['away']['name']
                                    estadio = jogo['fixture']['venue']['name']
                                    horario = data_jogo.strftime("%H:%M")
                                    competicao = jogo['league']['name']
                                    escudo_oponente = jogo['teams']['away']['logo'] if jogo['teams']['home']['id'] == BOTAFOGO_ID else jogo['teams']['home']['logo']
                                    
                                    embed = discord.Embed(
                                        title="🔥 HOJE TEM FOGÃO!",
                                        description=f"**{home} vs {away}**",
                                        color=0xFFFFFF # Branco
                                    )
                                    embed.add_field(name="🏆 Competição", value=competicao, inline=False)
                                    embed.add_field(name="🕒 Horário", value=f"{horario}", inline=True)
                                    embed.add_field(name="🏟️ Estádio", value=estadio, inline=True)
                                    embed.set_thumbnail(url=escudo_oponente) # Mostra o escudo do adversário
                                    embed.set_author(name="Botafogo de Futebol e Regatas", icon_url="https://upload.wikimedia.org/wikipedia/commons/c/cb/Botafogo_de_Futebol_e_Regatas_logo.svg")
                                    embed.set_footer(text="Exclusivo Fogão Zone • Notícias Automáticas")
                                    
                                    await canal.send(content="@everyone O GLORIOSO ENTRA EM CAMPO HOJE!", embed=embed)
            except Exception as e:
                print(f"Erro ao buscar jogo: {e}")

    @verificar_jogos.before_loop
    async def before_verificar(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Noticias(bot))