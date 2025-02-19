import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("El token de Discord no está configurado correctamente en el archivo .env")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

def print_bot_banner():
    print("\033[H\033[J", end="")
    print(
        "\033[0;34m████████╗ █████╗ ██╗   ██╗    ████████╗██╗ ██████╗██╗  ██╗███████╗████████╗███████╗\033[0m\n"
        "\033[1;34m╚══██╔══╝██╔══██╗╚██╗ ██╔╝    ╚══██╔══╝██║██╔════╝██║ ██╔╝██╔════╝╚══██╔══╝██╔════╝\033[0m\n"
        "\033[0;36m   ██║   ███████║ ╚████╔╝        ██║   ██║██║     █████╔╝ █████╗     ██║   ███████╗\033[0m\n"
        "\033[1;36m   ██║   ██╔══██║  ╚██╔╝         ██║   ██║██║     ██╔═██╗ ██╔══╝     ██║   ╚════██║\033[0m\n"
        "\033[1;36m   ██║   ██║  ██║   ██║          ██║   ██║╚██████╗██║  ██╗███████╗   ██║   ███████║\033[0m\n"
        "\033[1;35m   ╚═╝   ╚═╝  ╚═╝   ╚═╝          ╚═╝   ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝\033[0m"
    )

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            extension = f'cogs.{filename[:-3]}'
            try:
                await bot.load_extension(extension)
                print(f"Extensión {extension} cargada.")
            except Exception as e:
                handle_extension_error(extension, e)

def handle_extension_error(extension, error):
    error_messages = {
        commands.ExtensionNotFound: f"La extensión '{extension}' no se encontró.",
        commands.ExtensionAlreadyLoaded: f"La extensión '{extension}' ya está cargada.",
        commands.NoEntryPointError: f"La extensión '{extension}' no tiene un punto de entrada 'setup'.",
        commands.ExtensionFailed: f"La extensión '{extension}' falló al cargar. {error.original}",
    }
    print(error_messages.get(type(error), f"Error al cargar la extensión '{extension}': {error}"))

@bot.event
async def on_ready():
    print_bot_banner()
    print(f"🤖 Bot conectado como {bot.user}")
    await load_extensions()

bot.run(TOKEN)
