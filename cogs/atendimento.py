import discord
from discord.ext import commands
import asyncio

# =========================
# CONFIGURAÇÕES
# =========================
CANAL_PAINEL_ID = 1461419430335746240
CANAL_SUGESTOES_ID = 1461419803024556044

STAFF_ROLE_IDS = [
    1461301043458609273,
    1461298578231398436,
    1461297253435314289,
    1461294361710170249,
    1461071181217005620
]

# =========================
# VIEW DO TICKET (BOTÕES)
# =========================
class TicketView(discord.ui.View):
    def __init__(self, autor_id: int):
        super().__init__(timeout=None)
        self.autor_id = autor_id

    def is_staff(self, member: discord.Member) -> bool:
        return any(role.id in STAFF_ROLE_IDS for role in member.roles)

    @discord.ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.gray, row=0)
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.autor_id and not self.is_staff(interaction.user):
            await interaction.response.send_message(
                "❌ Você não tem permissão para fechar este ticket.",
                ephemeral=True
            )
            return

        autor = interaction.guild.get_member(self.autor_id)
        if autor:
            await interaction.channel.set_permissions(autor, view_channel=False)

        await interaction.response.send_message(
            "🔒 Ticket fechado. Apenas a staff pode vê-lo."
        )

    @discord.ui.button(label="🗑️ Excluir Ticket", style=discord.ButtonStyle.red, row=1)
    async def excluir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_staff(interaction.user):
            await interaction.response.send_message(
                "❌ Apenas a staff pode excluir o ticket.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🗑️ Ticket será excluído em 5 segundos..."
        )
        await asyncio.sleep(5)
        await interaction.channel.delete()

# =========================
# VIEW DO PAINEL (CORRIGIDA)
# =========================
class PainelAtendimento(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Selecione uma opção de atendimento",
        min_values=1,
        max_values=1,
        custom_id="painel_atendimento_select",
        options=[
            discord.SelectOption(label="Dúvidas Gerais", value="Dúvidas Gerais", emoji="❓"),
            discord.SelectOption(label="Denúncias", value="Denúncias", emoji="🚨"),
            discord.SelectOption(label="Solicitar punições", value="Solicitar punições", emoji="⚖️"),
            discord.SelectOption(label="Sugestões", value="Sugestões", emoji="💡"),
            discord.SelectOption(label="Bugs", value="Bugs", emoji="🐞"),
            discord.SelectOption(label="Patrocinar, parceria ou serviços", value="Parcerias", emoji="🤝"),
            discord.SelectOption(label="Minha opção não se encontra aqui", value="Outros", emoji="📌"),
        ]
    )
    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        # RESPONDE IMEDIATAMENTE PARA EVITAR "INTERAÇÃO FALHOU"
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        user = interaction.user
        escolha = select.values[0]

        # SUGESTÕES
        if escolha == "Sugestões":
            canal = guild.get_channel(CANAL_SUGESTOES_ID)
            mention = canal.mention if canal else "canal de sugestões"
            await interaction.followup.send(f"💡 Caso queira dar alguma sugestão, vá em {mention}", ephemeral=True)
            return

        # EVITA MÚLTIPLOS TICKETS
        if discord.utils.get(guild.text_channels, name=f"ticket-{user.id}"):
            await interaction.followup.send("❌ Você já possui um ticket aberto.", ephemeral=True)
            return

        # CATEGORIA SUPORTE
        categoria = next((c for c in guild.categories if "SUPORTE" in c.name.upper()), None)
        if not categoria:
            await interaction.followup.send("❌ Categoria SUPORTE não encontrada no servidor.", ephemeral=True)
            return

        # PERMISSÕES
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        for role_id in STAFF_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        # CRIAÇÃO DO CANAL
        try:
            canal = await guild.create_text_channel(
                name=f"ticket-{user.id}",
                category=categoria,
                overwrites=overwrites
            )

            embed = discord.Embed(
                title="📩 Ticket de Atendimento",
                description=(
                    f"Olá {user.mention}, seu ticket foi criado.\n\n"
                    f"**Motivo:** {escolha}\n\n"
                    "Descreva sua solicitação com o máximo de detalhes."
                ),
                color=discord.Color.dark_grey()
            )

            await canal.send(content=user.mention, embed=embed, view=TicketView(user.id))
            await interaction.followup.send(f"✅ Seu ticket foi criado: {canal.mention}", ephemeral=True)
            
        except Exception as e:
            print(f"Erro ao criar canal: {e}")
            await interaction.followup.send("❌ Ocorreu um erro ao tentar criar o canal do ticket.", ephemeral=True)

# =========================
# COG
# =========================
class Atendimento(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def painel(self, ctx):
        canal = self.bot.get_channel(CANAL_PAINEL_ID)
        if not canal:
            await ctx.send("❌ Canal do painel não encontrado. Verifique o ID nas configurações.")
            return

        embed = discord.Embed(
            title="📞 Central de Suporte",
            description=(
                "Selecione abaixo a opção que melhor descreve seu atendimento.\n\n"
                "Nossa equipe irá atendê-lo o mais breve possível."
            ),
            color=discord.Color.dark_grey()
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1389943081238925333/1468688412029489153/Painel_Atendimento_Fogao_Zone_6.png")

        await canal.send(embed=embed, view=PainelAtendimento())
        await ctx.send("✅ Painel enviado com sucesso!", delete_after=5)

async def setup(bot):
    await bot.add_cog(Atendimento(bot))