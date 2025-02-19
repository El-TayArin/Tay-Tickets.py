import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("\033[H\033[J", end="")
    print(
        "\033[0;34m████████╗ █████╗ ██╗   ██╗    ████████╗██╗ ██████╗██╗  ██╗███████╗████████╗███████╗\033[0m\n"
        "\033[1;34m╚══██╔══╝██╔══██╗╚██╗ ██╔╝    ╚══██╔══╝██║██╔════╝██║ ██╔╝██╔════╝╚══██╔══╝██╔════╝\033[0m\n"
        "\033[0;36m   ██║   ███████║ ╚████╔╝        ██║   ██║██║     █████╔╝ █████╗     ██║   ███████╗\033[0m\n"
        "\033[1;36m   ██║   ██╔══██║  ╚██╔╝         ██║   ██║██║     ██╔═██╗ ██╔══╝     ██║   ╚════██║\033[0m\n"
        "\033[1;36m   ██║   ██║  ██║   ██║          ██║   ██║╚██████╗██║  ██╗███████╗   ██║   ███████║\033[0m\n"
        "\033[1;35m   ╚═╝   ╚═╝  ╚═╝   ╚═╝          ╚═╝   ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝\033[0m"
    )
    print(f"🤖 Bot conectado como {bot.user}")
    # Cargar la extensión
    await bot.load_extension("cogs.tickets")

bot.run(TOKEN)
