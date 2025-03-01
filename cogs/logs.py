import json
from datetime import datetime
import discord
from discord.ext import commands


def load_json(file, default_data=None):
    try:
        with open(file, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_data if default_data is not None else {}


def save_json(file, data):
    try:
        with open(file, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except (FileNotFoundError, OSError, json.JSONDecodeError) as e:
        print(f"⚠️ Error al guardar {file}: {e}")


class TicketLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_json('config.json', {})
        self.log_channel_id = int(self.config.get("log_channel_id", 0))
        self.tickets = load_json('tickets.json', {})

    def get_log_channel(self):
        return self.bot.get_channel(self.log_channel_id)

    async def log_ticket_creation(self, user: discord.Member, category: str, channel: discord.TextChannel):
        log_channel = self.get_log_channel()
        if log_channel:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            self.tickets[channel.id] = {
                "opened_by": user.id,
                "category": category,
                "opened_at": timestamp
            }
            save_json('tickets.json', self.tickets)

            embed = discord.Embed(title="📌 Ticket Creado",
                                  color=discord.Color.green())
            embed.add_field(name="Usuario", value=user.mention, inline=True)
            embed.add_field(name="Categoría", value=category, inline=True)
            embed.add_field(name="Canal", value=channel.mention, inline=False)
            embed.add_field(name="Fecha de Apertura",
                            value=timestamp, inline=False)
            embed.set_footer(text=f"Ticket ID: {channel.id}")
            await log_channel.send(embed=embed)

    async def log_ticket_closure(self, user: discord.Member, channel: discord.TextChannel):
        log_channel = self.get_log_channel()
        if log_channel and channel.id in self.tickets:
            ticket_data = self.tickets[channel.id]
            opened_by = self.bot.get_user(ticket_data["opened_by"])
            category = ticket_data["category"]
            opened_at = ticket_data["opened_at"]
            closed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')

            embed = discord.Embed(title="🔒 Ticket Cerrado",
                                  color=discord.Color.red())
            embed.add_field(
                name="Abierto por",
                value=opened_by.mention if opened_by else "Desconocido",
                inline=True
            )
            embed.add_field(name="Cerrado por",
                            value=user.mention, inline=True)
            embed.add_field(name="Categoría", value=category, inline=False)
            embed.add_field(name="Fecha de Apertura",
                            value=opened_at, inline=False)
            embed.add_field(name="Fecha de Cierre",
                            value=closed_at, inline=False)
            embed.set_footer(text=f"Ticket ID: {channel.id}")
            await log_channel.send(embed=embed)

            del self.tickets[channel.id]
            save_json('tickets.json', self.tickets)

    async def log_ticket_claim(self, user: discord.Member, channel: discord.TextChannel):
        log_channel = self.get_log_channel()
        if log_channel and channel.id in self.tickets:
            claimed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')

            embed = discord.Embed(title="👤 Ticket Reclamado",
                                  color=discord.Color.yellow())
            embed.add_field(name="Reclamado por",
                            value=user.mention, inline=True)
            embed.add_field(name="Canal", value=channel.mention, inline=False)
            embed.add_field(name="Fecha de Reclamo",
                            value=claimed_at, inline=False)
            embed.set_footer(text=f"Ticket ID: {channel.id}")
            await log_channel.send(embed=embed)

    async def log_ticket_release(self, user: discord.Member, channel: discord.TextChannel):
        log_channel = self.get_log_channel()
        if log_channel and channel.id in self.tickets:
            released_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')

            embed = discord.Embed(title="🔓 Ticket Liberado",
                                  color=discord.Color.orange())
            embed.add_field(name="Liberado por",
                            value=user.mention, inline=True)
            embed.add_field(name="Canal", value=channel.mention, inline=False)
            embed.add_field(name="Fecha de Liberación",
                            value=released_at, inline=False)
            embed.set_footer(text=f"Ticket ID: {channel.id}")
            await log_channel.send(embed=embed)


async def setup(bot):
    print("🔁 Cargando el sistema de logs...")
    await bot.add_cog(TicketLogs(bot))
    print("✅ Sistema de logs cargado correctamente.")
