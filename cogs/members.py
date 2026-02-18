import discord
from discord.ext import commands

# =========================
# CONFIGURAÇÕES DE LOGS
# =========================
# Troque pelos IDs dos canais onde você quer que as mensagens apareçam
CANAL_BEM_VINDO_ID = 1473648806641012797
CANAL_SAIU_ID = 1473648806641012797

class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Evento: Quando um membro ENTRA
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.get_channel(CANAL_BEM_VINDO_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="👋 Bem-vindo(a)!",
            description=f"Olá {member.mention}, seja muito bem-vindo(a) ao **{member.guild.name}**!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Membro nº", value=str(member.guild.member_count))
        embed.set_footer(text=f"ID do usuário: {member.id}")

        await channel.send(embed=embed)

    # Evento: Quando um membro SAI
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.get_channel(CANAL_SAIU_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="💔 Alguém saiu",
            description=f"O membro **{member.name}** saiu do servidor.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Agora somos", value=f"{member.guild.member_count} membros")
        embed.set_footer(text=f"ID do usuário: {member.id}")

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Members(bot))