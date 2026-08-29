from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands

# Salons et Rôles configurés
TARGET_CHANNEL_ID = 1542238377837989888

# Catégories selon les choix
CATEGORY_PURCHASE = 1542287551069425695
CATEGORY_SUPPORT = 1542288367600009357
CATEGORY_STAFF = 1542288454950592552

# Rôles autorisés pour la commande /ticket et les accès aux tickets
ALLOWED_ROLE_ID = 1542206470970671214
ROLE_STAFF_2 = 1542289291399528570


class CloseTicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.primary,
        emoji="<:lock2:1542305185462882304>",
        custom_id="close_ticket_button",
    )
    async def close_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🔒 Fermeture du ticket en cours...", ephemeral=True
        )
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"Erreur lors de la suppression du salon: {e}")


class TicketModal(discord.ui.Modal, title="Support Question"):
    issue = discord.ui.TextInput(
        label="What is your issue?",
        style=discord.TextStyle.paragraph,
        placeholder="Describe your issue in detail here...",
        required=True,
        max_length=2000,
    )

    def __init__(self, bot, footer_text, bot_avatar):
        super().__init__()
        self.bot = bot
        self.footer_text = footer_text
        self.bot_avatar = bot_avatar

    async def on_submit(self, interaction: discord.Interaction):
        await TicketView.handle_ticket_creation(
            interaction, self.bot, "Support", CATEGORY_SUPPORT, self.issue.value
        )


class TicketSelect(discord.ui.Select):

    def __init__(self, bot, footer_text, bot_avatar):
        self.bot = bot
        self.footer_text = footer_text
        self.bot_avatar = bot_avatar

        options = [
            discord.SelectOption(
                label="Purchase",
                description="Purchase coins or products",
                emoji="<:cart:1542297234404802570>",
                value="purchase",
            ),
            discord.SelectOption(
                label="Support",
                description=(
                    "Product assistance or any inquiries regarding the service"
                ),
                emoji="<:support:1542297461748539432>",
                value="support",
            ),
            discord.SelectOption(
                label="Staff",
                description="Submit your application to join the staff team",
                emoji="<:staff:1542297826476695582>",
                value="staff",
            ),
        ]
        super().__init__(
            placeholder="Select your ticket category…",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        valeur = self.values[0]

        if valeur == "purchase":
            await TicketView.handle_ticket_creation(
                interaction, self.bot, "Purchase", CATEGORY_PURCHASE
            )
        elif valeur == "support":
            modal = TicketModal(self.bot, self.footer_text, self.bot_avatar)
            await interaction.response.send_modal(modal)
        elif valeur == "staff":
            await TicketView.handle_ticket_creation(
                interaction, self.bot, "Staff", CATEGORY_STAFF
            )


class TicketView(discord.ui.View):

    def __init__(self, bot, footer_text, bot_avatar):
        super().__init__(timeout=None)
        self.add_item(TicketSelect(bot, footer_text, bot_avatar))

    @staticmethod
    async def handle_ticket_creation(
        interaction: discord.Interaction,
        bot,
        ticket_type: str,
        category_id: int,
        modal_content: str = None,
    ):
        guild = interaction.guild
        user = interaction.user

        existing_channel = None
        for channel in guild.text_channels:
            if channel.name == user.name.lower() and channel.category_id in [
                CATEGORY_PURCHASE,
                CATEGORY_SUPPORT,
                CATEGORY_STAFF,
            ]:
                existing_channel = channel
                break
            elif (
                channel.category_id
                in [CATEGORY_PURCHASE, CATEGORY_SUPPORT, CATEGORY_STAFF]
                and channel.overwrites.get(user)
                and channel.overwrites.get(user).read_messages
            ):
                existing_channel = channel
                break

        if existing_channel:
            if not interaction.response.is_done():
                return await interaction.response.send_message(
                    f"❌ You already have an open ticket here: {existing_channel.mention}",
                    ephemeral=True,
                )
            else:
                return await interaction.followup.send(
                    f"❌ You already have an open ticket here: {existing_channel.mention}",
                    ephemeral=True,
                )

        category = guild.get_channel(category_id)
        role_staff1 = guild.get_role(ALLOWED_ROLE_ID)
        role_staff2 = guild.get_role(ROLE_STAFF_2)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(
                read_messages=True, send_messages=True, manage_channels=True, manage_messages=True
            ),
            user: discord.PermissionOverwrite(
                read_messages=True, send_messages=True, view_channel=True
            ),
        }

        if role_staff1:
            overwrites[role_staff1] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, view_channel=True
            )
        if role_staff2:
            overwrites[role_staff2] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, view_channel=True
            )

        channel_name = user.name.lower()

        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name, category=category, overwrites=overwrites
            )
        except Exception as e:
            if not interaction.response.is_done():
                return await interaction.response.send_message(
                    f"❌ An error occurred while creating the ticket channel: {e}",
                    ephemeral=True,
                )
            else:
                return await interaction.followup.send(
                    f"❌ An error occurred while creating the ticket channel: {e}",
                    ephemeral=True,
                )

        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"✅ Your ticket has been created successfully: {ticket_channel.mention}",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                f"✅ Your ticket has been created successfully: {ticket_channel.mention}",
                ephemeral=True,
            )

        bot_avatar = bot.user.display_avatar.url if bot.user else None
        bot_name = bot.user.name if bot.user else "Bot"
        now_str = datetime.now().strftime("%d/%m/%Y at %H:%M")
        footer_text = f"{bot_name} | {now_str}"

        embed_ticket = discord.Embed(color=discord.Color.from_str("#0058ff"))

        if ticket_type == "Purchase":
            embed_ticket.title = (
                "<:ticket:1542297746550161448> Ticket purchase created !"
            )
            embed_ticket.description = (
                "We are delighted that you have opened a support ticket with us !\n\n"
                "Please provide us with the details of your order ; we will respond as"
                " quickly as possible to assist you and meet your needs. If you have"
                " any issues or specific questions regarding our products, please let"
                " us know."
            )
        elif ticket_type == "Support":
            embed_ticket.title = (
                "<:ticket:1542297746550161448> Ticket Support created !"
            )
            embed_ticket.description = (
                "Thank you for opening a ticket ; we are happy to help !\n\nYour issue"
                f" is :\n```\n{modal_content}\n```\nWe will get back to you as soon"
                " as possible to assist you and address your needs."
            )
        elif ticket_type == "Staff":
            embed_ticket.title = (
                "<:ticket:1542297746550161448> Ticket Support created !"
            )
            embed_ticket.description = (
                "Thank you for opening a **ticket** ; we are delighted to welcome you"
                " to our **team** !\n\nPlease let us know your **reasons** for wanting"
                " to join the team, your **availability**, and your country's **UTC"
                " time zone**.\n\nWe will try to get back to you as **soon as"
                " possible**."
            )

        if bot_avatar:
            embed_ticket.set_footer(text=footer_text, icon_url=bot_avatar)
        else:
            embed_ticket.set_footer(text=footer_text)

        close_view = CloseTicketView()
        sent_message = await ticket_channel.send(
            content="@everyone", embed=embed_ticket, view=close_view
        )
        try:
            await sent_message.pin()
        except Exception:
            pass


class Ticket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ticket",
        description="Display the ticket creation panel in the designated channel.",
    )
    async def ticket(self, interaction: discord.Interaction):
        bot_avatar = self.bot.user.display_avatar.url if self.bot.user else None
        bot_name = self.bot.user.name if self.bot.user else "Bot"
        now_str = datetime.now().strftime("%d/%m/%Y at %H:%M")
        footer_text = f"{bot_name} | {now_str}"

        user_role_ids = [role.id for role in interaction.user.roles]
        if ALLOWED_ROLE_ID not in user_role_ids:
            embed_refuse = discord.Embed(
                title="<:info:1542297839026053190> Access denied",
                description=(
                    "You do not have the required **permissions** to use"
                    " this **command**. This **action** is restricted to **staff**."
                ),
                color=discord.Color.from_str("#0058ff"),
            )
            if bot_avatar:
                embed_refuse.set_footer(text=footer_text, icon_url=bot_avatar)
            else:
                embed_refuse.set_footer(text=footer_text)
            return await interaction.response.send_message(
                embed=embed_refuse, ephemeral=True
            )

        target_channel = interaction.guild.get_channel(TARGET_CHANNEL_ID)

        embed_panel = discord.Embed(
            title="<:ticket:1542297746550161448> Open a Ticket",
            description=(
                "To open a **ticket**, please choose the **correct category** below"
                " that aligns with your **request**. Each ticket should address a"
                " **single subject**, so ensure you select the most **relevant**"
                " one.\n\n<:tos:1542297487346376834> **__Ticket Guidelines__ :**"
                "\n\n• Do not open **multiple tickets**.\n\n• List your **issue"
                " carefully** with all **details**, **screenshots**, and"
                " **videos** to help us fix it **qicker** & **better**.\n\n• "
                "**Corporation** is 100% required, failure to do so we will"
                " simply will help you. Please make this easier for both of"
                " us.\n\n• Please be **kind** & have **respect** as we will do the"
                " same!"
            ),
            color=discord.Color.from_str("#0058ff"),
        )

        if bot_avatar:
            embed_panel.set_footer(text=footer_text, icon_url=bot_avatar)
        else:
            embed_panel.set_footer(text=footer_text)

        view = TicketView(self.bot, footer_text, bot_avatar)

        destination = target_channel if target_channel else interaction.channel

        await destination.send(embed=embed_panel, view=view)

        if interaction.channel.id != TARGET_CHANNEL_ID:
            await interaction.response.send_message(
                f"✅ Ticket panel successfully sent to {destination.mention}!",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "✅ Ticket panel successfully sent!", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Ticket(bot))