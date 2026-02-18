import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Importante: Verifique se o caminho da cog de atendimento está correto
from cogs.atendimento import PainelAtendimento  

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True # Adicionado para garantir que ele veja os canais

class FogaoBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        # Carregando as extensões corretamente usando self
        await self.load_extension("cogs.atendimento")
        await self.load_extension("cogs.parcerias")
        await self.load_extension("cogs.xp")
        await self.load_extension("members.py")
        
        try:
            await self.load_extension("cogs.noticias")
            print("--- [OK] Cog de Noticias carregada com sucesso! ---")
        except Exception as e:
            print(f"--- [ERRO] Falha ao carregar a cog de noticias: {e} ---")

        # Registra a view persistente
        self.add_view(PainelAtendimento())

bot = FogaoBot()

# Apenas UM on_ready com tudo dentro
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"--- BOT LIGADO: {bot.user} ---")
    print("--- TUDO ONLINE E SINCRONIZADO ---")

# Rodar o bot
token = os.getenv("TOKEN")
if token:
    bot.run(token)
else:
    print("ERRO: TOKEN não encontrado nas variáveis de ambiente!")