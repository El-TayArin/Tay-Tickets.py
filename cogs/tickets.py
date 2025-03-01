import asyncio
import json
import discord
from discord.ext import commands
from discord.ui import Select, View, Button, Modal, TextInput
from cogs.logs import TicketLogs


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


class TicketDropdown(Select):
    def __init__(self, bot, interaction, ticket_categories):
        self.bot = bot
        self.interaction = interaction
        self.ticket_categories = ticket_categories
        options = [discord.SelectOption(label=cat_data["display_name"], value=cat)
                   for cat, cat_data in ticket_categories.items()]
        super().__init__(
            placeholder=self.bot.lang["category_selection_description"], options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        guild = interaction.guild
        ticket_name = f"ticket-{interaction.user.name}".lower()

        if ticket_name in self.bot.ticket_system.tickets:
            embed = discord.Embed(
                title=self.bot.lang["ticket_error_title"],
                description=self.bot.lang["ticket_already_open_error"],
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        category_data = self.ticket_categories[category]
        category_id = int(category_data["category_id"])
        category_obj = discord.utils.get(guild.categories, id=category_id)
        if not category_obj:
            embed = discord.Embed(
                title=self.bot.lang["ticket_error_title"],
                description=self.bot.lang["category_not_found_error"],
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        support_role_id = int(category_data["support_role_id"])
        support_role = guild.get_role(support_role_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True),
        }

        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(ticket_name, overwrites=overwrites, category=category_obj)
        self.bot.ticket_system.tickets[ticket_name] = {
            "channel_id": ticket_channel.id, "claimed_by": None}
        self.bot.ticket_system.save_tickets()
        await self.bot.ticket_system.ticket_logs.log_ticket_creation(interaction.user, category, ticket_channel)
        view = View()
        view.add_item(CloseTicketButton(self.bot, ticket_channel))
        view.add_item(ClaimTicketButton(self.bot, ticket_channel))
        view.add_item(AddUserButton(self.bot, ticket_channel))

        embed = discord.Embed(
            title=self.bot.lang["ticket_opened_title"],
            description=self.bot.lang["ticket_opened"].format(
                user_mention=interaction.user.mention, category_display_name=category_data['display_name']),
            color=discord.Color.green()
        )
        await ticket_channel.send(embed=embed, view=view)

        embed_response = discord.Embed(
            title=self.bot.lang["ticket_created_title"],
            description=self.bot.lang["ticket_created"].format(
                category_display_name=category_data['display_name'], ticket_channel_mention=ticket_channel.mention),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed_response, ephemeral=True)


class TicketButton(Button):
    def __init__(self, bot, ticket_categories):
        super().__init__(
            label=bot.lang["buttons"]["open_ticket"], style=discord.ButtonStyle.primary)
        self.bot = bot
        self.ticket_categories = ticket_categories

    async def callback(self, interaction: discord.Interaction):
        view = View()
        view.add_item(TicketDropdown(
            self.bot, interaction, self.ticket_categories))
        embed = discord.Embed(title=self.bot.lang["category_selection_title"],
                              description=self.bot.lang["category_selection_description"],
                              color=discord.Color.blue()
                              )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class CloseTicketButton(Button):
    def __init__(self, bot, ticket_channel):
        super().__init__(
            label=bot.lang["buttons"]["close_ticket"], style=discord.ButtonStyle.danger)
        self.bot = bot
        self.ticket_channel = ticket_channel

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title=self.bot.lang["close_ticket"],
                              description=self.bot.lang["close_ticket_description"],
                              color=discord.Color.red()
                              )
        await self.ticket_channel.send(embed=embed)
        ticket_name = self.ticket_channel.name
        if ticket_name in self.bot.ticket_system.tickets:
            del self.bot.ticket_system.tickets[ticket_name]
            self.bot.ticket_system.save_tickets()
        await self.bot.ticket_system.ticket_logs.log_ticket_closure(interaction.user, self.ticket_channel)
        await asyncio.sleep(5)
        await self.ticket_channel.delete()


class ClaimTicketButton(Button):
    def __init__(self, bot, ticket_channel):
        super().__init__(
            label=bot.lang["buttons"]["claim_ticket"], style=discord.ButtonStyle.success)
        self.bot = bot
        self.ticket_channel = ticket_channel

    async def callback(self, interaction: discord.Interaction):
        ticket_name = self.ticket_channel.name
        ticket_data = self.bot.ticket_system.tickets.get(ticket_name)

        if ticket_data is None:
            await interaction.response.send_message("No se encontró información del ticket.", ephemeral=True)
            return

        if ticket_data["claimed_by"] is None:
            ticket_data["claimed_by"] = interaction.user.id
            self.bot.ticket_system.save_tickets()

            self.label = self.bot.lang["buttons"]["release_ticket"]
            self.style = discord.ButtonStyle.secondary

            embed = discord.Embed(
                title=self.bot.lang["ticket_claimed_title"],
                description=self.bot.lang["ticket_claimed"].format(
                    user_mention=interaction.user.mention),
                color=discord.Color.green()
            )
            await self.ticket_channel.send(embed=embed)

            await self.bot.ticket_system.ticket_logs.log_ticket_claim(interaction.user, self.ticket_channel)

        elif ticket_data["claimed_by"] == interaction.user.id:
            ticket_data["claimed_by"] = None
            self.bot.ticket_system.save_tickets()

            self.label = self.bot.lang["buttons"]["claim_ticket"]
            self.style = discord.ButtonStyle.success

            embed = discord.Embed(
                title=self.bot.lang["ticket_released_title"],
                description=self.bot.lang["ticket_released"].format(
                    user_mention=interaction.user.mention),
                color=discord.Color.yellow()
            )
            await self.ticket_channel.send(embed=embed)

            await self.bot.ticket_system.ticket_logs.log_ticket_release(interaction.user, self.ticket_channel)
        else:
            await interaction.response.send_message(self.bot.lang["ticket_already_claimed"], ephemeral=True)

        await interaction.message.edit(view=self.view)


class AddUserButton(Button):
    def __init__(self, bot, ticket_channel):
        super().__init__(
            label=bot.lang["buttons"]["add_user"], style=discord.ButtonStyle.secondary)
        self.bot = bot
        self.ticket_channel = ticket_channel

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(self.bot.lang["no_permission"], ephemeral=True)
            return

        modal = AddUserModal(self.bot, self.ticket_channel)
        await interaction.response.send_modal(modal)


class AddUserModal(Modal):
    def __init__(self, bot, ticket_channel):
        self.bot = bot
        super().__init__(title=self.bot.lang["user_add_modal_title"])
        self.ticket_channel = ticket_channel
        self.user_id = TextInput(
            label=self.bot.lang["user_add_modal_label"], placeholder=self.bot.lang["user_add_modal_placeholder"])
        self.add_item(self.user_id)

    async def on_submit(self, interaction: discord.Interaction, /):
        user_id = int(self.user_id.value)
        user = interaction.guild.get_member(user_id)
        if user:
            await self.ticket_channel.set_permissions(user, read_messages=True, send_messages=True)
            await interaction.response.send_message(self.bot.lang["user_added"].format(user_mention=user.mention))
        else:
            await interaction.response.send_message(self.bot.lang["user_not_found"], ephemeral=True)


class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_json('config.json', {})
        self.tickets = load_json('tickets.json', {})
        self.tickets_channel_id = int(self.config.get("ticket_channel_id", 0))
        self.ticket_categories = self.config.get("ticket_categories", {})
        self.ticket_message = self.config.get(
            "ticket_message", "Presiona el botón para abrir un ticket.")
        self.ticket_logs = TicketLogs(bot)
        bot.ticket_system = self

    def save_tickets(self):
        save_json('tickets.json', self.tickets)

    async def send_ticket_message(self):
        await asyncio.sleep(5)
        channel = self.bot.get_channel(self.tickets_channel_id)
        if channel:
            await channel.purge(limit=10)
            view = View()
            view.add_item(TicketButton(self.bot, self.ticket_categories))
            embed = discord.Embed(title=self.bot.lang["ticket_system_title"],
                                  description=self.bot.lang["ticket_system_description"], color=discord.Color.blue())
            await channel.send(embed=embed, view=view)

    @commands.command(name="setup_tickets")
    async def setup_tickets(self, ctx):
        if ctx.author.guild_permissions.administrator:
            await self.send_ticket_message()
            embed = discord.Embed(title=self.bot.lang["setup_complete_title"],
                                  description=self.bot.lang["setup_complete"],
                                  color=discord.Color.green()
                                  )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=self.bot.lang["setup_perms_error_title"],
                description=self.bot.lang["setup_perms_error"],
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


async def setup(bot):
    print("🔁 Cargando el sistema de tickets...")
    ticket_system = TicketSystem(bot)
    await bot.add_cog(ticket_system)
    await ticket_system.send_ticket_message()
    print("✅ Sistema de tickets cargado correctamente.")
