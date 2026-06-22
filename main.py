import random
import discord
from discord import app_commands
import json
import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "Phantom Bot Online!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

CONFIG_FILE = "config.json"


def carregar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "canal_sugestoes": None,
        "canal_logs": None
    }


def salvar_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


config = carregar_config()


class SugestaoView(discord.ui.View):
    def __init__(self, mensagem_publica_id):
        super().__init__(timeout=3600)
        self.mensagem_publica_id = mensagem_publica_id

    @discord.ui.button(label="Aceitar", emoji="✅", style=discord.ButtonStyle.green)
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):

        canal_publico = interaction.client.get_channel(config["canal_sugestoes"])

        try:
            mensagem_publica = await canal_publico.fetch_message(self.mensagem_publica_id)

            embed = mensagem_publica.embeds[0]
            embed.color = discord.Color.green()

            embed.set_field_at(
                0,
                name="Status",
                value="✅ APROVADA",
                inline=False
            )

            await mensagem_publica.edit(embed=embed)

        except:
            pass

        await interaction.message.edit(view=None)

        await interaction.response.send_message("✅ Sugestão aprovada!", ephemeral=True)

    @discord.ui.button(label="Recusar", emoji="❌", style=discord.ButtonStyle.red)
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button):

        canal_publico = interaction.client.get_channel(config["canal_sugestoes"])

        try:
            mensagem_publica = await canal_publico.fetch_message(self.mensagem_publica_id)

            embed = mensagem_publica.embeds[0]
            embed.color = discord.Color.red()

            embed.set_field_at(
                0,
                name="Status",
                value="❌ RECUSADA",
                inline=False
            )

            await mensagem_publica.edit(embed=embed)

        except:
            pass

        await interaction.message.edit(view=None)

        await interaction.response.send_message("❌ Sugestão recusada!", ephemeral=True)


class MeuPrimeiroBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"✅ BOT {self.user} iniciado com sucesso!")


bot = MeuPrimeiroBot()

# ===============================
# PHANTOM
# ===============================
@bot.tree.command(name="phantom", description="Primeiro comando do BOT")
async def phantom(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Olá, {interaction.user.mention}! Eu sou o Phantom!"
    )


# ===============================
# SOMA
# ===============================
@bot.tree.command(name="soma", description="Soma dois números")
async def soma(interaction: discord.Interaction, numero1: int, numero2: int):
    resultado = numero1 + numero2

    await interaction.response.send_message(
        f"🧮 {numero1} + {numero2} = **{resultado}**",
        ephemeral=True
    )


# ===============================
# CONFIG SUGESTÃO
# ===============================
@bot.tree.command(name="configurar_sugestao", description="Configurar canais")
@app_commands.default_permissions(administrator=True)
async def configurar_sugestao(interaction: discord.Interaction, canal_sugestoes: discord.TextChannel, canal_logs: discord.TextChannel):

    config["canal_sugestoes"] = canal_sugestoes.id
    config["canal_logs"] = canal_logs.id

    salvar_config(config)

    await interaction.response.send_message(
        f"✅ Sistema configurado!\n📋 Sugestões: {canal_sugestoes.mention}\n📝 Logs: {canal_logs.mention}",
        ephemeral=True
    )


# ===============================
# AVISO
# ===============================
@bot.tree.command(name="aviso", description="Enviar aviso")
@app_commands.default_permissions(administrator=True)
async def aviso(interaction: discord.Interaction, titulo: str, mensagem: str, ping: bool = False):

    embed = discord.Embed(
        title=f"🚨 {titulo.upper()} 🚨",
        description=mensagem,
        color=discord.Color.from_rgb(255, 60, 60)
    )

    embed.add_field(
        name="━━━━━━━━━━━━━━━━━━━━━━",
        value="📢 Sistema Oficial de Avisos",
        inline=False
    )

    embed.set_footer(text=f"📌 Aviso enviado por {interaction.user}")

    content = "@everyone ⚠️ Novo aviso importante!" if ping else None

    await interaction.channel.send(content=content, embed=embed)

    await interaction.response.send_message("✅ Aviso enviado!", ephemeral=True)


# ===============================
# BOT RUN (CORRETO)
# ===============================
bot.run(os.getenv("DISCORD_TOKEN"))
