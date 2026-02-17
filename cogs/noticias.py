import discord
from discord.ext import commands, tasks
import os

class Noticias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enviar_teste_imediato.start()

    def cog_unload(self):
        self.enviar_teste_imediato.cancel()

    @tasks.loop(count=1) # Roda apenas UMA vez ao ligar
    async def enviar_teste_imediato(self):
        await self.bot.wait_until_ready()
        print("--- [DEBUG] Tentando enviar mensagem de teste... ---")
        
        CANAL_ID = 1461311054368739464
        canal = self.bot.get_channel(CANAL_ID)
        
        if canal:
            try:
                await canal.send("✅ **SISTEMA DE NOTÍCIAS ONLINE!** Se você ler isso, o bot finalmente conectou com o canal.")
                print("--- [DEBUG] Mensagem enviada com sucesso! ---")
            except Exception as e:
                print(f"--- [DEBUG] Erro ao enviar no canal: {e} ---")
        else:
            print(f"--- [DEBUG] Não encontrei o canal com ID {CANAL_ID}. Verifique as permissões!")

async def setup(bot):
    await bot.add_cog(Noticias(bot))