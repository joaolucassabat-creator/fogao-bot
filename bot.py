import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()




intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class FogaoBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        # Carrega o cog de atendimento
        await self.load_extension("cogs.atendimento")
        await bot.load_extension("cogs.parcerias")



bot = FogaoBot()


@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")


TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)

