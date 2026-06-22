import discord
from discord import app_commands
import json
import os
import logging

logging.basicConfig(level=logging.INFO)

CONFIG_FILE = "config.json"


# ===============================
# CONFIG
# ===============================
def carregar_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Erro ao carregar config:", e)

    return {
        "canal_sugestoes": None,
        "canal_logs": None
    }


def salvar_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print("Erro ao salvar config:", e)


config = carregar_config()


# ===============================
# VIEW SUGESTÃO
# ===============================
class SugestaoView(discord.ui.View):
    def __init__(self, mensagem_publica_id: int):
        super().__init__(timeout=3600)
        self.mensagem_publica_id = mensagem_publica_id

    @discord.ui.button(label="Aceitar", emoji="✅", style=discord.ButtonStyle.green)
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):

        canal_id = config.get("canal_sugestoes")
        if not canal_id:
            return await interaction.response.send_message("❌ Canal não configurado.", ephemeral=True)

        canal = interaction.client.get_channel(canal_id)
        if not canal:
            return await interaction.response.send_message("❌ Canal não encontrado.", ephemeral=True)

        try:
            mensagem = await canal.fetch_message(self.mensagem_publica_id)

            if not mensagem.embeds:
                return await interaction.response.send_message("❌ Embed inválido.", ephemeral=True)

            embed = mensagem.embeds[0]
            embed.color = discord.Color.green()
            embed.set_field_at(0, name="Status", value="✅ APROVADA", inline=False)

            await mensagem.edit(embed=embed)

            await interaction.message.edit(view=None)
            await interaction.response.send_message("✅ Sugestão aprovada!", ephemeral=True)

        except Exception as e:
            print("Erro aceitar sugestão:", e)
            await interaction.response.send_message("❌ Erro ao aprovar.", ephemeral=True)

    @discord.ui.button(label="Recusar", emoji="❌", style=discord.ButtonStyle.red)
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button):

        canal_id = config.get("canal_sugestoes")
        if not canal_id:
            return await interaction.response.send_message("❌ Canal não configurado.", ephemeral=True)

        canal = interaction.client.get_channel(canal_id)
        if not canal:
            return await interaction.response.send_message("❌ Canal não encontrado.", ephemeral=True)

        try:
            mensagem = await canal.fetch_message(self.mensagem_publica_id)

            if not mensagem.embeds:
                return await interaction.response.send_message("❌ Embed inválido.", ephemeral=True)

            embed = mensagem.embeds[0]
            embed.color = discord.Color.red()
            embed.set_field_at(0, name="Status", value="❌ RECUSADA", inline=False)

            await mensagem.edit(embed=embed)

            await interaction.message.edit(view=None)
            await interaction.response.send_message("❌ Sugestão recusada!", ephemeral=True)

        except Exception as e:
            print("Erro recusar sugestão:", e)
            await interaction.response.send_message("❌ Erro ao recusar.", ephemeral=True)


# ===============================
# BOT
# ===============================
class MeuPrimeiroBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash commands sincronizados")

    async def on_ready(self):
        print(f"✅ BOT {self.user} iniciado com sucesso!")


bot = MeuPrimeiroBot()


# ===============================
# TOKEN (SEM CRASH)
# ===============================
TOKEN = os.getenv("DISCORD_TOKEN")


# ===============================
# COMANDOS
# ===============================
@bot.tree.command(name="soma", description="Calcula uma expressão")
async def soma(interaction: discord.Interaction, expressao: str):
    try:
        resultado = eval(expressao)

        await interaction.response.send_message(
            f"🧮 O Resultado de {expressao} = é **{resultado}**",
            ephemeral=True
        )
    except:
        await interaction.response.send_message(
            "❌ Expressão inválida!",
            ephemeral=True
        )


@bot.tree.command(name="configurar_sugestao", description="Configurar canais")
@app_commands.default_permissions(administrator=True)
async def configurar_sugestao(interaction: discord.Interaction,
    canal_sugestoes: discord.TextChannel,
    canal_logs: discord.TextChannel
):

    config["canal_sugestoes"] = canal_sugestoes.id
    config["canal_logs"] = canal_logs.id
    salvar_config(config)

    await interaction.response.send_message(
        f"✅ Sistema configurado!\n📋 Sugestões: {canal_sugestoes.mention}\n📝 Logs: {canal_logs.mention}",
        ephemeral=True
    )


@bot.tree.command(name="aviso", description="Enviar aviso")
@app_commands.default_permissions(administrator=True)
async def aviso(interaction: discord.Interaction, titulo: str, mensagem: str, ping: bool = False):

    embed = discord.Embed(
        title=f"🚨 {titulo.upper()} 🚨",
        description=mensagem,
        color=discord.Color.red()
    )

    embed.add_field(
        name="Sistema Oficial",
        value="📢 Aviso automático do servidor",
        inline=False
    )

    embed.set_footer(text=f"Por {interaction.user}")

    content = "@everyone ⚠️ Novo aviso!" if ping else None

    await interaction.channel.send(content=content, embed=embed)
    await interaction.response.send_message("✅ Aviso enviado!", ephemeral=True)


# ===============================
# RUN
# ===============================
if not TOKEN:
    print("❌ DISCORD_TOKEN não configurado no Render")
else:
    bot.run(TOKEN)
