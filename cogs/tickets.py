import json
import asyncio
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

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_json('config.json', {})
        self.tickets = load_json('tickets.json', {})
        self.tickets_channel_id = int(self.config.get("ticket_channel_id", 0))
        self.category_id = int(self.config.get("category_id", 0))

    def save_tickets(self):
        save_json('tickets.json', self.tickets)

    def is_ticket_creation_channel(self, ctx):
        return ctx.channel.id == self.tickets_channel_id

    def is_ticket_channel(self, ctx):
        return ctx.channel.name.startswith("ticket-")

    @commands.command(name="ticket")
    async def create_ticket(self, ctx):
        if not self.is_ticket_creation_channel(ctx):
            return

        guild = ctx.guild
        ticket_name = f"ticket-{ctx.author.name}"

        if ticket_name in self.tickets:
            await ctx.send("❌ ¡Ya tienes un ticket abierto! Cierra el anterior antes de abrir uno nuevo.")
            return

        category = discord.utils.get(guild.categories, id=self.category_id)
        if not category:
            await ctx.send("⚠️ No se ha encontrado la categoría para los tickets.")
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        ticket_channel = await guild.create_text_channel(ticket_name, overwrites=overwrites, category=category)
        self.tickets[ticket_name] = ticket_channel.id
        self.save_tickets()

        await ticket_channel.send(f"🎫 ¡Hola {ctx.author.mention}! Este es tu ticket. Un miembro del equipo te atenderá pronto.")
        await ctx.send(f"✅ ¡Tu ticket ha sido creado! Accede a él en: {ticket_channel.mention}")

    @commands.command(name="close")
    async def close_ticket(self, ctx):
        if not self.is_ticket_channel(ctx):
            await ctx.send("❌ No puedes cerrar un ticket fuera de su canal.")
            return

        ticket_name = ctx.channel.name

        if ticket_name in self.tickets:
            ticket_channel = self.bot.get_channel(self.tickets[ticket_name])
            if ticket_channel:
                await ctx.send(f"🔒 El ticket {ticket_channel.name} se cerrará en 5 segundos...")
                del self.tickets[ticket_name]
                self.save_tickets()
                await asyncio.sleep(5)
                await ctx.send(f"✅ El ticket {ticket_channel.name} ha sido cerrado.")
                await asyncio.sleep(2)
                await ticket_channel.delete()
        else:
            await ctx.send("❌ No tienes un ticket abierto o no estás en el canal correcto.")

async def setup(bot):
    print("🔁 Cargando el sistema de tickets...")
    await bot.add_cog(TicketSystem(bot))
    print("✅ Sistema de tickets cargado correctamente.")
    