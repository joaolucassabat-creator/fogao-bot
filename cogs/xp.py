import discord
from discord.ext import commands
import json
import os
import random

# =============================
# CONFIGURAÇÃO DO BOT
# =============================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =============================
# CONFIGURAÇÃO DOS CARGOS (DO MAIOR PARA O MENOR)
# =============================

LEVEL_ROLES = {
    15: 1461311054368739464,
    14: 1461310873837633761,
    13: 1461310572065849415,
    12: 1461310395213156407,
    11: 1461310182041845815,
    10: 1461309970715902015,
    9: 1461309629140308104,
    8: 1461309381348950199,
    7: 1461309179800059971,
    6: 1461309027832037476,
    5: 1461308733111144489,
    4: 1461308193065013258,
    3: 1461308013968101428,
    2: 1461307812612276405,
    1: 1461307537725853696
}

# =============================
# SISTEMA DE ARMAZENAMENTO
# =============================

if not os.path.exists("xp.json"):
    with open("xp.json", "w") as f:
        json.dump({}, f)


def load_data():
    with open("xp.json", "r") as f:
        return json.load(f)


def save_data(data):
    with open("xp.json", "w") as f:
        json.dump(data, f, indent=4)


def calculate_level(xp):
    return int(xp ** 0.5)


# =============================
# EVENTO DE MENSAGEM
# =============================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    data = load_data()
    user_id = str(message.author.id)

    if user_id not in data:
        data[user_id] = {"xp": 0, "level": 0}

    old_level = data[user_id]["level"]

    # Ganha XP aleatório
    xp_gain = random.randint(5, 15)
    data[user_id]["xp"] += xp_gain

    new_level = calculate_level(data[user_id]["xp"])
    data[user_id]["level"] = new_level

    save_data(data)

    # Se subiu de nível
    if new_level > old_level:
        await update_roles(message.author, new_level)

        embed = discord.Embed(
            title="⚫⚪ SUBIU DE NÍVEL! ⚪⚫",
            description=f"{message.author.mention} agora é **Nível {new_level}**!\n\n🔥 O FOGÃO TÁ VOANDO! 🔥",
            color=discord.Color.dark_grey()
        )

        await message.channel.send(embed=embed)

    await bot.process_commands(message)


# =============================
# FUNÇÃO PARA ATUALIZAR CARGOS
# =============================

async def update_roles(member, level):

    guild = member.guild

    # Remove todos os cargos de rank
    for role_id in LEVEL_ROLES.values():
        role = guild.get_role(role_id)
        if role in member.roles:
            await member.remove_roles(role)

    # Adiciona o cargo correto (maior possível)
    for lvl in sorted(LEVEL_ROLES.keys(), reverse=True):
        if level >= lvl:
            role_id = LEVEL_ROLES[lvl]
            role = guild.get_role(role_id)
            await member.add_roles(role)
            break


# =============================
# COMANDO PARA VER RANK
# =============================

@bot.command()
async def rank(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    data = load_data()
    user_id = str(member.id)

    if user_id not in data:
        await ctx.send("Esse usuário ainda não tem XP.")
        return

    xp = data[user_id]["xp"]
    level = data[user_id]["level"]

    embed = discord.Embed(
        title=f"⚫⚪ Rank de {member.display_name} ⚪⚫",
        color=discord.Color.dark_grey()
    )

    embed.add_field(name="Nível", value=level)
    embed.add_field(name="XP", value=xp)

    await ctx.send(embed=embed)


# =============================
# INICIAR BOT
# =============================


bot.run(os.getenv("TOKEN"))

