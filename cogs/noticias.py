import discord
from discord.ext import commands, tasks
import aiohttp
import os
from datetime import datetime

class Noticias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verificar_jogos.start()

    def cog_unload(self):
        self.verificar_jogos.cancel()

    @tasks.loop(count=1) # Roda uma vez ao ligar para testarmos agora
    async def verificar_jogos(self):
        await self.bot.wait_until_ready()
        
        # --- CONFIGURAÇÕES ---
        CANAL_ID = 1461344345289654292
        BOTAFOGO_ID = 134  
        API_KEY = os.getenv("FOOTBALL_API_KEY")
        
        # Tenta pegar o canal da memória ou busca direto no servidor
        canal = self.bot.get_channel(CANAL_ID)
        if not canal:
            try:
                canal = await self.bot.fetch_channel(CANAL_ID)
            except:
                print(f"--- [ERRO] Não foi possível encontrar o canal {CANAL_ID} ---")
                return

        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        
        url = f"https://v3.football.api-sports.io/fixtures?team={BOTAFOGO_ID}&next=1"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()
                    if data.get('response'):
                        jogo = data['response'][0]
                        
                        home = jogo['teams']['home']['name']
                        away = jogo['teams']['away']['name']
                        estadio = jogo['fixture']['venue']['name']
                        data_str = jogo['fixture']['date']
                        data_obj = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
                        
                        # Formatação
                        horario = data_obj.strftime("%H:%M")
                        dia = data_obj.strftime("%d/%m")
                        
                        escudo_op = jogo['teams']['away']['logo'] if jogo['teams']['home']['id'] == BOTAFOGO_ID else jogo['teams']['home']['logo']
                        
                        embed = discord.Embed(
                            title="🔥 PRÓXIMO JOGO DO GLORIOSO",
                            description=f"**{home} vs {away}**",
                            color=0x000000
                        )
                        embed.add_field(name="📅 Data", value=dia, inline=True)
                        embed.add_field(name="🕒 Horário", value=horario, inline=True)
                        embed.add_field(name="🏟️ Estádio", value=estadio, inline=False)
                        embed.set_thumbnail(url=escudo_op)
                        embed.set_author(name="Botafogo de Futebol e Regatas", icon_url="https://upload.wikimedia.org/wikipedia/commons/c/cb/Botafogo_de_Futebol_e_Regatas_logo.svg")
                        embed.set_footer(text="Setorista Automático Fogão Zone")
                        
                        await canal.send(content="📢 **O Setorista chegou!** Confira os detalhes do próximo jogo:", embed=embed)
                        print("--- [OK] Notícia enviada com sucesso! ---")
            except Exception as e:
                print(f"--- [ERRO] Falha na API ou envio: {e} ---")

    @verificar_jogos.before_loop
    async def before_verificar(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Noticias(bot))