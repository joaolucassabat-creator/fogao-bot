import discord
from discord.ext import commands
import asyncio

# =========================
# CONFIGURAÇÕES
# =========================
CANAL_PAINEL_ID = 1461419430335746240
CANAL_SUGESTOES_ID = 1461419803024556044
CANAL_LOGS_TICKETS_ID = 1472196203457544347  # 👈 COLOQUE O ID DO CANAL DE LOGS AQUI

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

    @discord.ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.gray, row=0, custom_id="btn_fechar")
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.autor_id and not self.is_staff(interaction.user):
            await interaction.response.send_message("❌ Você não tem permissão para fechar este ticket.", ephemeral=True)
            return

        autor = interaction.guild.get_member(self.autor_id)
        if autor:
            await interaction.channel.set_permissions(autor, view_channel=False)

        await interaction.response.send_message("🔒 Ticket fechado. Apenas a staff pode vê-lo.")

        # --- LOG DE FECHAMENTO ---
        log_channel = interaction.guild.get_channel(CANAL_LOGS_TICKETS_ID)
        if log_channel:
            log_embed = discord.Embed(title="🔒 Ticket Fechado", color=discord.Color.orange(), timestamp=discord.utils.utcnow())
            log_embed.add_field(name="Responsável", value=interaction.user.mention)
            log_embed.add_field(name="Canal", value=interaction.channel.mention)
            log_embed.add_field(name="Dono do Ticket", value=f"<@{self.autor_id}>")
            await log_channel.send(embed=log_embed)

    @discord.ui.button(label="🗑️ Excluir Ticket", style=discord.ButtonStyle.red, row=1, custom_id="btn_excluir")
    async def excluir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_staff(interaction.user):
            await interaction.response.send_message("❌ Apenas a staff pode excluir o ticket.", ephemeral=True)
            return

        # --- LOG DE EXCLUSÃO (ANTES DE DELETAR) ---
        log_channel = interaction.guild.get_channel(CANAL_LOGS_TICKETS_ID)
        if log_channel:
            log_embed = discord.Embed(title="🗑️ Ticket Excluído", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            log_embed.add_field(name="Excluído por", value=interaction.user.mention)
            log_embed.add_field(name="Nome do Canal", value=interaction.channel.name)
            await log_channel.send(embed=log_embed)

        await interaction.response.send_message("🗑️ Ticket será excluído em 5 segundos...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

# =========================
# VIEW DO PAINEL
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
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        user = interaction.user
        escolha = select.values[0]

        if escolha == "Sugestões":
            canal = guild.get_channel(CANAL_SUGESTOES_ID)
            mention = canal.mention if canal else "canal de sugestões"
            await interaction.followup.send(f"💡 Caso queira dar alguma sugestão, vá em {mention}", ephemeral=True)
            return

        if discord.utils.get(guild.text_channels, name=f"ticket-{user.id}"):
            await interaction.followup.send("❌ Você já possui um ticket aberto.", ephemeral=True)
            return

        categoria = next((c for c in guild.categories if "SUPORTE" in c.name.upper()), None)
        if not categoria:
            await interaction.followup.send("❌ Categoria SUPORTE não encontrada.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        for role_id in STAFF_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        try:
            canal = await guild.create_text_channel(name=f"ticket-{user.id}", category=categoria, overwrites=overwrites)
            
            embed = discord.Embed(
                title="📩 Ticket de Atendimento",
                description=f"Olá {user.mention}, seu ticket foi criado.\n\n**Motivo:** {escolha}\n\nDescreva sua solicitação com detalhes.",
                color=discord.Color.dark_grey()
            )

            await canal.send(content=user.mention, embed=embed, view=TicketView(user.id))
            await interaction.followup.send(f"✅ Seu ticket foi criado: {canal.mention}", ephemeral=True)

            # --- LOG DE ABERTURA ---
            log_channel = guild.get_channel(CANAL_LOGS_TICKETS_ID)
            if log_channel:
                log_embed = discord.Embed(title="🎫 Ticket Aberto", color=discord.Color.green(), timestamp=discord.utils.utcnow())
                log_embed.add_field(name="Usuário", value=f"{user.mention} ({user.id})", inline=False)
                log_embed.add_field(name="Motivo", value=escolha, inline=False)
                log_embed.add_field(name="Canal", value=canal.mention, inline=False)
                await log_channel.send(embed=log_embed)

        except Exception as e:
            print(f"Erro: {e}")
            await interaction.followup.send("❌ Erro ao criar o ticket.", ephemeral=True)

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
            await ctx.send("❌ Canal do painel não encontrado.")
            return

        embed = discord.Embed(
            title="📞 Central de Suporte",
            description="Selecione abaixo a opção que melhor descreve seu atendimento.",
            color=discord.Color.dark_grey()
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1389943081238925333/1468688412029489153/Painel_Atendimento_Fogao_Zone_6.png")

        await canal.send(embed=embed, view=PainelAtendimento())
        await ctx.send("✅ Painel enviado!", delete_after=5)

async def setup(bot):
    await bot.add_cog(Atendimento(bot))