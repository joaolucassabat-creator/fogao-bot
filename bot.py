import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()


TOKEN = "MTQ2MTAxMTA4MTI0MDc3MjY5OQ.G6e8oT.XvHRK6F9pEA6HTKg-wmXjspbr14zd51Y91_00Q"

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

