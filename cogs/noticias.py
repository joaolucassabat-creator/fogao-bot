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

    @tasks.loop(minutes=5) # Diminuí o tempo para o teste ser rápido
    async def verificar_jogos(self):
        print("--- [DEBUG] Iniciando checagem de jogos ---")
        CANAL_ID = 1461311054368739464 # <--- Verifique se esse ID está 100% certo
        BOTAFOGO_ID = 120
        API_KEY = os.getenv("FOOTBALL_API_KEY")
        
        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        
        url = f"https://v3.football.api-sports.io/fixtures?team={BOTAFOGO_ID}&next=1"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as resp:
                    print(f"--- [DEBUG] Status da API: {resp.status} ---")
                    data = await resp.json()
                    
                    if not data.get('response'):
                        print(f"--- [DEBUG] API não retornou jogos para o ID {BOTAFOGO_ID}. Verifique o ID. ---")
                        return

                    jogo = data['response'][0]
                    home = jogo['teams']['home']['name']
                    away = jogo['teams']['away']['name']
                    print(f"--- [DEBUG] Jogo encontrado: {home} vs {away} ---")

                    canal = self.bot.get_channel(CANAL_ID)
                    if canal is None:
                        print(f"--- [DEBUG] ERRO: Não encontrei o canal com ID {CANAL_ID}. O bot tem acesso a ele? ---")
                        return

                    # TESTE FORÇADO: Vamos mandar a mensagem sem nenhuma condição de data
                    embed = discord.Embed(
                        title="🔥 TESTE DE NOTÍCIA",
                        description=f"Próximo Jogo: **{home} vs {away}**",
                        color=0xFFFFFF
                    )
                    await canal.send(content="Teste de conexão do setorista!", embed=embed)
                    print("--- [DEBUG] Mensagem enviada com sucesso! ---")

            except Exception as e:
                print(f"--- [DEBUG] ERRO CRÍTICO: {e} ---")

    @verificar_jogos.before_loop
    async def before_verificar(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Noticias(bot))