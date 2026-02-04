import discord
from discord.ext import commands

class Parcerias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def parcerias(self, ctx):
        embed = discord.Embed(
            title="🤝 Parcerias & Patrocínios – Fogão Zone",
            description=(
                "Tem interesse em divulgar seu projeto, serviço ou marca em parceria com o **Fogão Zone**?\n\n"
                "Estamos abertos a propostas de:\n"
                "• Parcerias\n"
                "• Patrocínios\n"
                "• Divulgação de serviços\n"
                "• Colaborações em geral\n\n"
                "📩 **Como entrar em contato:**\n"
                "Abra um ticket no painel de atendimento e selecione a opção\n"
                "**“Patrocinar, parceria ou serviços”**, descrevendo sua proposta com o máximo de detalhes.\n\n"
                "Nossa equipe irá analisar e responder o mais breve possível. 🔥🖤🤍"
            ),
            color=discord.Color.dark_grey()
        )

        # Quando criar a imagem, é só descomentar e colocar o link
        embed.set_image(url="https://media.discordapp.net/attachments/1389943081238925333/1468697824412700906/PATROCIONIOS_E_PARCERIAS_FOGAO_ZONE.png?ex=6984f6f0&is=6983a570&hm=976cb71e6debb8052079e7b973a775c469a0ccb81646c5a4486479f6b74aec1b&=&format=webp&quality=lossless&width=967&height=544")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Parcerias(bot))
