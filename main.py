import random

import discord
from discord import app_commands
import json
import os
from flask import Flask
from threading import Thread
import os

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

    @discord.ui.button(
        label="Aceitar",
        emoji="✅",
        style=discord.ButtonStyle.green
    )
    async def aceitar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        canal_publico = interaction.client.get_channel(
            config["canal_sugestoes"]
        )

        try:
            mensagem_publica = await canal_publico.fetch_message(
                self.mensagem_publica_id
            )

            embed = mensagem_publica.embeds[0]

            embed.color = discord.Color.green()

            embed.set_field_at(
                0,
                name="Status",
                value="✅ APROVADA",
                inline=False
            )

            await mensagem_publica.edit(
                embed=embed
            )

        except:
            pass

        await interaction.message.edit(
            view=None
        )

        await interaction.response.send_message(
            "✅ Sugestão aprovada!",
            ephemeral=True
        )

    @discord.ui.button(
        label="Recusar",
        emoji="❌",
        style=discord.ButtonStyle.red
    )
    async def recusar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        canal_publico = interaction.client.get_channel(
            config["canal_sugestoes"]
        )

        try:
            mensagem_publica = await canal_publico.fetch_message(
                self.mensagem_publica_id
            )

            embed = mensagem_publica.embeds[0]

            embed.color = discord.Color.red()

            embed.set_field_at(
                0,
                name="Status",
                value="❌ RECUSADA",
                inline=False
            )

            await mensagem_publica.edit(
                embed=embed
            )

        except:
            pass

        await interaction.message.edit(
            view=None
        )

        await interaction.response.send_message(
            "❌ Sugestão recusada!",
            ephemeral=True
        )


class MeuPrimeiroBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()

        super().__init__(
            intents=intents
        )

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(
            f"✅ BOT {self.user} iniciado com sucesso!"
        )



bot = MeuPrimeiroBot()

# ===============================
# PHANTOM BOT
# ===============================
@bot.tree.command(
    name="phantom_bot",
    description="Primeiro comando do BOT"
)
)
async def phantombot(
    interaction: discord.Interaction
):
    await interaction.response.send_message(
        f"Olá, {interaction.user.mention}! Eu sou o Phantom BOT!"
    )


# ===============================
# SOMA
# ===============================

@bot.tree.command(
    name="soma",
    description="Soma dois números"
)
async def soma(
    interaction: discord.Interaction,
    numero1: int,
    numero2: int
):
    resultado = numero1 + numero2

    await interaction.response.send_message(
        f"🧮 {numero1} + {numero2} = **{resultado}**",
        ephemeral=True
    )


# ===============================
# CONFIGURAR SUGESTÃO
# ===============================

@bot.tree.command(
    name="configurar_sugestao",
    description="Configurar canais de sugestões"
)
@app_commands.default_permissions(
    administrator=True
)
async def configurar_sugestao(
    interaction: discord.Interaction,
    canal_sugestoes: discord.TextChannel,
    canal_logs: discord.TextChannel
):
    config["canal_sugestoes"] = canal_sugestoes.id
    config["canal_logs"] = canal_logs.id

    salvar_config(config)

    await interaction.response.send_message(
        f"✅ Sistema configurado!\n\n"
        f"📋 Sugestões: {canal_sugestoes.mention}\n"
        f"📝 Logs: {canal_logs.mention}",
        ephemeral=True
    )




# ===============================
# AVISO
# ===============================

@bot.tree.command(
    name="aviso",
    description="Enviar um aviso estilizado"
)
@app_commands.default_permissions(administrator=True)
async def aviso(
    interaction: discord.Interaction,
    titulo: str,
    mensagem: str,
    ping: bool = False
):

    # 🎨 Cor bonita fixa (vermelho moderno)
    cor = discord.Color.from_rgb(255, 60, 60)

    embed = discord.Embed(
        title=f"🚨 {titulo.upper()} 🚨",
        description=mensagem,
        color=cor
    )

    # ✨ Linha de destaque
    embed.add_field(
        name="━━━━━━━━━━━━━━━━━━━━━━",
        value="📢 Sistema Oficial de Avisos",
        inline=False
    )

    embed.set_footer(
        text=f"📌 Aviso enviado por {interaction.user}"
    )

    embed.set_thumbnail(
        url=interaction.guild.icon.url if interaction.guild.icon else None
    )

    # 🔔 Ping invisível (fica abaixo do embed)
    content = "@everyone ⚠️ Novo aviso importante!" if ping else None

    await interaction.channel.send(
        content=content,
        embed=embed
    )

    await interaction.response.send_message(
        "✅ Aviso enviado com sucesso!",
        ephemeral=True
    )


# ===============================
# ENVIAR SUGESTÃO
# ===============================

@bot.tree.command(
    name="sugestao",
    description="Enviar uma sugestão"
)
async def sugestao(
    interaction: discord.Interaction,
    mensagem: str
):
    
    canal_publico = bot.get_channel(
        config["canal_sugestoes"]
    )

    canal_logs = bot.get_channel(
        config["canal_logs"]
    )

    embed_publico = discord.Embed(
        title="📋 Sugestão",
        description=mensagem,
        color=discord.Color.yellow()
    )

    embed_publico.add_field(
        name="Status",
        value="⏳ EM ANÁLISE",
        inline=False
    )

    embed_publico.add_field(
        name="Autor",
        value=interaction.user.mention,
        inline=False
    )

    mensagem_publica = await canal_publico.send(
        embed=embed_publico
    )

    embed_logs = discord.Embed(
        title="📋 Nova Sugestão",
        description=mensagem,
        color=discord.Color.orange()
    )

    embed_logs.add_field(
        name="Autor",
        value=interaction.user.mention,
        inline=False
    )

    await canal_logs.send(
        embed=embed_logs,
        view=SugestaoView(
            mensagem_publica.id
        )
    )

    await interaction.response.send_message(
        "✅ Sugestão enviada!",
        ephemeral=True
    )


import os

bot.run(os.getenv("DISCORD_TOKEN"))
