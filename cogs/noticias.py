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

    @tasks.loop(hours=24)
    async def verificar_jogos(self):
        # --- CONFIGURAÇÕES ---
        CANAL_ID = 1461311054368739464 
        BOTAFOGO_ID = 134  # ID oficial do Botafogo (RJ)
        API_KEY = os.getenv("FOOTBALL_API_KEY")
        
        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        
        # Pega o próximo jogo
        url = f"https://v3.football.api-sports.io/fixtures?team={BOTAFOGO_ID}&next=1"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('response'):
                            jogo = data['response'][0]
                            
                            # PARA O TESTE: Ignoramos a data e postamos o próximo jogo encontrado
                            canal = self.bot.get_channel(CANAL_ID)
                            if canal:
                                home = jogo['teams']['home']['name']
                                away = jogo['teams']['away']['name']
                                estadio = jogo['fixture']['venue']['name']
                                data_str = jogo['fixture']['date']
                                data_obj = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
                                horario = data_obj.strftime("%H:%M")
                                data_formatada = data_obj.strftime("%d/%02m")
                                
                                # Escudo do oponente
                                escudo_op = jogo['teams']['away']['logo'] if jogo['teams']['home']['id'] == BOTAFOGO_ID else jogo['teams']['home']['logo']
                                
                                embed = discord.Embed(
                                    title="🔥 PRÓXIMO JOGO DO GLORIOSO",
                                    description=f"**{home} vs {away}**",
                                    color=0x000000 # Preto
                                )
                                embed.add_field(name="📅 Data", value=data_formatada, inline=True)
                                embed.add_field(name="🕒 Horário", value=horario, inline=True)
                                embed.add_field(name="🏟️ Estádio", value=estadio, inline=False)
                                embed.set_thumbnail(url=escudo_op)
                                embed.set_author(name="Botafogo de Futebol e Regatas", icon_url="https://upload.wikimedia.org/wikipedia/commons/c/cb/Botafogo_de_Futebol_e_Regatas_logo.svg")
                                embed.set_footer(text="Setorista Automático Fogão Zone")
                                
                                await canal.send(content="📢 **Atenção!** O próximo jogo já está marcado:", embed=embed)
            except Exception as e:
                print(f"Erro ao postar notícia: {e}")

@tasks.loop(minutes=1) # Curto para testar rápido
async def verificar_jogos(self):
        CANAL_ID = 1461311054368739464
        canal = self.bot.get_channel(CANAL_ID)
        
        print(f"--- [DEBUG] Tentando contato com o canal {CANAL_ID} ---")
        
        if canal is None:
            print(f"--- [DEBUG] O bot NÃO ENCONTROU o canal. Verifique se o ID está certo! ---")
            # Tenta buscar o canal de outra forma se o get_channel falhar
            try:
                canal = await self.bot.fetch_channel(CANAL_ID)
                print("--- [DEBUG] Canal encontrado usando fetch_channel! ---")
            except:
                print("--- [DEBUG] Falha total ao encontrar o canal. ---")
                return

        try:
            await canal.send("🚨 **TESTE DE CONEXÃO DO BOT!** Se você está lendo isso, o bot tem permissão!")
            print("--- [DEBUG] Mensagem de texto enviada! Partindo para a API... ---")
        except Exception as e:
            print(f"--- [DEBUG] O bot encontrou o canal mas NÃO CONSEGUIU enviar mensagem: {e} ---")
            return

        # ... (resto do código da API que já temos)
async def setup(bot):
    await bot.add_cog(Noticias(bot))