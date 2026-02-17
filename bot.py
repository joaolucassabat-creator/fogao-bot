import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio


from cogs.atendimento import PainelAtendimento  # 👈 IMPORTANTE

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
        await self.load_extension("cogs.atendimento")
        await self.load_extension("cogs.parcerias")
        await self.load_extension("cogs.xp")


        # 👇 REGISTRA A VIEW PERSISTENTE
        self.add_view(PainelAtendimento())


bot = FogaoBot()



@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Conectado como {bot.user}")



import os

bot.run(os.getenv("TOKEN"))

