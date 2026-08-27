from datetime import datetime
import json
import os
import random
import string
import discord
from discord import app_commands
from discord.ext import commands
from aiohttp import web

# Rôles autorisés pour la commande /invoice
ALLOWED_ROLE_ID = 1542206470970671214

# Dictionnaire global pour stocker les factures en attente de paiement
PENDING_INVOICES = {}


class AddProductModal(discord.ui.Modal, title="Add a product"):
    product_name = discord.ui.TextInput(
        label="Product name",
        style=discord.TextStyle.paragraph,
        placeholder="Enter product name...",
        required=True,
        max_length=500,
    )
    price = discord.ui.TextInput(
        label="Price",
        style=discord.TextStyle.short,
        placeholder="Enter price...",
        required=True,
        max_length=50,
    )
    quantity = discord.ui.TextInput(
        label="Quantity",
        style=discord.TextStyle.short,
        placeholder="Enter quantity...",
        required=True,
        max_length=50,
    )

    def __init__(self, view_instance):
        super().__init__()
        self.view_instance = view_instance

    async def on_submit(self, interaction: discord.Interaction):
        self.view_instance.products.append(
            {
                "name": self.product_name.value,
                "price": self.price.value,
                "quantity": self.quantity.value,
            }
        )
        await self.view_instance.update_message(interaction)


class EditProductModal(discord.ui.Modal, title="Edit a product"):
    product_name = discord.ui.TextInput(
        label="Product name",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500,
    )
    price = discord.ui.TextInput(
        label="Price", style=discord.TextStyle.short, required=True, max_length=50
    )
    quantity = discord.ui.TextInput(
        label="Quantity",
        style=discord.TextStyle.short,
        required=True,
        max_length=50,
    )

    def __init__(self, view_instance, index):
        super().__init__()
        self.view_instance = view_instance
        self.index = index
        prod = view_instance.products[index]
        self.product_name.default = prod["name"]
        self.price.default = prod["price"]
        self.quantity.default = prod["quantity"]

    async def on_submit(self, interaction: discord.Interaction):
        self.view_instance.products[self.index] = {
            "name": self.product_name.value,
            "price": self.price.value,
            "quantity": self.quantity.value,
        }
        await self.view_instance.update_message(interaction)


class InvoiceSelectMenu(discord.ui.Select):

    def __init__(self, parent_view, mode="main"):
        self.parent_view = parent_view
        self.mode = mode
        options = []

        if mode == "main":
            options = [
                discord.SelectOption(
                    label="Add a product from invoice",
                    emoji="<:add:1542564459925741608>",
                    value="add_prod",
                ),
                discord.SelectOption(
                    label="Remove a product from invoice",
                    emoji="<:remove:1542564590074855525>",
                    value="remove_prod",
                ),
                discord.SelectOption(
                    label="Edit a product from invoice",
                    emoji="<:edit:1542564664192409631>",
                    value="edit_prod",
                ),
            ]
            placeholder = "Choose your option…"
        elif mode == "remove_list":
            for idx, p in enumerate(parent_view.products):
                options.append(
                    discord.SelectOption(
                        label=p["name"][:100],
                        description=f"Price: {p['price']} € | Qty: {p['quantity']}",
                        emoji="<:arrow:1542297262544130168>",
                        value=f"rm_{idx}",
                    )
                )
            options.append(
                discord.SelectOption(
                    label="Back to menu",
                    emoji="<:back:1542638431598022770>",
                    value="back_to_menu",
                )
            )
            placeholder = "Select a product to remove…"
        elif mode == "edit_list":
            for idx, p in enumerate(parent_view.products):
                options.append(
                    discord.SelectOption(
                        label=p["name"][:100],
                        description=f"Price: {p['price']} € | Qty: {p['quantity']}",
                        emoji="<:arrow:1542297262544130168>",
                        value=f"ed_{idx}",
                    )
                )
            options.append(
                discord.SelectOption(
                    label="Back to menu",
                    emoji="<:back:1542638431598022770>",
                    value="back_to_menu",
                )
            )
            placeholder = "Select a product to edit…"
        elif mode == "channels":
            for channel in parent_view.interaction.guild.text_channels[:25]:
                options.append(
                    discord.SelectOption(
                        label=channel.name[:100],
                        value=f"chan_{channel.id}",
                    )
                )
            if not options:
                options.append(
                    discord.SelectOption(label="No channels", value="none")
                )
            placeholder = "Select destination channel…"

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]

        if self.mode == "main":
            if val == "add_prod":
                modal = AddProductModal(self.parent_view)
                await interaction.response.send_modal(modal)
            elif val == "remove_prod":
                if not self.parent_view.products:
                    error_embed = discord.Embed(
                        title="**<:info:1542297839026053190> Error**",
                        description="There are **no products** added to the **invoice** yet.",
                        color=discord.Color.from_str("#ff0000"),
                    )
                    if self.parent_view.bot_avatar:
                        error_embed.set_footer(
                            text=self.parent_view.footer_text,
                            icon_url=self.parent_view.bot_avatar,
                        )
                    else:
                        error_embed.set_footer(
                            text=self.parent_view.footer_text
                        )
                    return await interaction.response.send_message(
                        embed=error_embed, ephemeral=True
                    )
                self.parent_view.mode = "remove_list"
                self.parent_view.refresh_components()
                await interaction.response.edit_message(
                    view=self.parent_view
                )
            elif val == "edit_prod":
                if not self.parent_view.products:
                    error_embed = discord.Embed(
                        title="**<:info:1542297839026053190> Error**",
                        description="There are **no products** added to the **invoice** yet.",
                        color=discord.Color.from_str("#ff0000"),
                    )
                    if self.parent_view.bot_avatar:
                        error_embed.set_footer(
                            text=self.parent_view.footer_text,
                            icon_url=self.parent_view.bot_avatar,
                        )
                    else:
                        error_embed.set_footer(
                            text=self.parent_view.footer_text
                        )
                    return await interaction.response.send_message(
                        embed=error_embed, ephemeral=True
                    )
                self.parent_view.mode = "edit_list"
                self.parent_view.refresh_components()
                await interaction.response.edit_message(
                    view=self.parent_view
                )
        elif self.mode == "remove_list":
            if val == "back_to_menu":
                self.parent_view.mode = "main"
                self.parent_view.refresh_components()
                await interaction.response.edit_message(
                    view=self.parent_view
                )
            elif val.startswith("rm_"):
                idx = int(val.split("_")[1])
                if idx < len(self.parent_view.products):
                    self.parent_view.products.pop(idx)
                
                if not self.parent_view.products:
                    self.parent_view.mode = "main"
                else:
                    self.parent_view.mode = "remove_list"
                
                self.parent_view.refresh_components()
                await self.parent_view.update_message(interaction)
        elif self.mode == "edit_list":
            if val == "back_to_menu":
                self.parent_view.mode = "main"
                self.parent_view.refresh_components()
                await interaction.response.edit_message(
                    view=self.parent_view
                )
            elif val.startswith("ed_"):
                idx = int(val.split("_")[1])
                modal = EditProductModal(self.parent_view, idx)
                await interaction.response.send_modal(modal)
        elif self.mode == "channels":
            if val.startswith("chan_"):
                chan_id = int(val.split("_")[1])
                target_chan = interaction.guild.get_channel(chan_id)
                if target_chan:
                    await self.parent_view.send_final_invoice(
                        interaction, target_chan
                    )
                else:
                    await interaction.response.send_message(
                        "❌ Salon introuvable.", ephemeral=True
                    )


class InvoiceView(discord.ui.View):

    def __init__(self, interaction, target_user, footer_text, bot_avatar):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.target_user = target_user
        self.footer_text = footer_text
        self.bot_avatar = bot_avatar
        self.products = []
        self.mode = "main"
        self.sending_mode = False
        self.refresh_components()

    def refresh_components(self):
        self.clear_items()
        if not self.sending_mode:
            self.add_item(InvoiceSelectMenu(self, mode=self.mode))
            self.add_item(SendInvoiceButton())
        else:
            self.add_item(InvoiceSelectMenu(self, mode="channels"))
            self.add_item(BackMenuButton())

    def build_embed(self):
        embed = discord.Embed(
            title="**<:info:1542297839026053190> Invoice management :**",
            description=(
                "You are **currently** on the **invoice management page** !"
                " <:stars:1542297435664154695>\n\nUsing the **selection menu**"
                " below this message, you can **add**, **modify**, or"
                " **remove** a product from the invoice."
            ),
            color=discord.Color.from_str("#0058ff"),
        )

        if self.products:
            names_col = []
            prices_col = []
            qtys_col = []

            for p in self.products:
                names_col.append(f"`{p['name']}`")
                prices_col.append(f"`{p['price']} €`")
                qtys_col.append(f"`{p['quantity']}`")

            embed.add_field(
                name="<:box:1542297038283079770> Product",
                value="\n".join(names_col),
                inline=True,
            )
            embed.add_field(
                name="<:price:1542297290411081778> Price",
                value="\n".join(prices_col),
                inline=True,
            )
            embed.add_field(
                name="<:quantity:1542640024623783946> Quantity",
                value="\n".join(qtys_col),
                inline=True,
            )

        if self.bot_avatar:
            embed.set_footer(text=self.footer_text, icon_url=self.bot_avatar)
        else:
            embed.set_footer(text=self.footer_text)
        return embed

    async def update_message(self, interaction: discord.Interaction):
        self.mode = "main"
        self.sending_mode = False
        self.refresh_components()
        embed = self.build_embed()
        if interaction.response.is_done():
            await interaction.edit_original_response(
                embed=embed, view=self
            )
        else:
            await interaction.response.edit_message(embed=embed, view=self)

    async def send_final_invoice(self, interaction: discord.Interaction, target_chan):
        total = 0
        names_col = []
        prices_col = []
        qtys_col = []

        for p in self.products:
            names_col.append(f"`{p['name']}`")
            prices_col.append(f"`{p['price']} €`")
            qtys_col.append(f"`{p['quantity']}`")
            try:
                clean_price = (
                    p["price"]
                    .replace("€", "")
                    .replace("$", "")
                    .replace(",", ".")
                    .strip()
                )
                unit_price = float(clean_price)
                total += unit_price
            except Exception:
                pass

        if total.is_integer():
            total_str = str(int(total))
        else:
            total_str = str(total)

        random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        payment_desc = f"Order INV-{random_suffix}"

        final_embed = discord.Embed(
            title="**<:invoice:1542562223891812413> New invoice created !**",
            description=(
                f"A **staff member** has created an **invoice** for"
                f" {self.target_user.mention} regarding an **order** they"
                " placed with us.\n\n<:invoice_details:1542640219495604254> **__Invoice details__ :**"
            ),
            color=discord.Color.from_str("#0058ff"),
        )

        if self.products:
            final_embed.add_field(
                name="<:box:1542297038283079770> Product",
                value="\n".join(names_col),
                inline=True,
            )
            final_embed.add_field(
                name="<:price:1542297290411081778> Price",
                value="\n".join(prices_col),
                inline=True,
            )
            final_embed.add_field(
                name="<:quantity:1542640024623783946> Quantity",
                value="\n".join(qtys_col),
                inline=True,
            )

        final_embed.add_field(
            name="\u200b",
            value=(
                f"The **total price** of your **order** is :\n\n"
                f"```{total_str} €```\n\n"
                f"<:info:1542297839026053190> Please **check carefully**"
                " for any **errors**; if you find a **mistake**, please let"
                " us know so we can **issue a new one**."
            ),
            inline=False,
        )

        if self.bot_avatar:
            final_embed.set_footer(
                text=self.footer_text, icon_url=self.bot_avatar
            )
        else:
            final_embed.set_footer(text=self.footer_text)

        class NextButtonView(discord.ui.View):

            def __init__(self, parent_view, total_str, payment_desc):
                super().__init__(timeout=None)
                self.parent_view = parent_view
                self.total_str = total_str
                self.payment_desc = payment_desc

            @discord.ui.button(
                label="Next",
                style=discord.ButtonStyle.secondary,
                emoji="<:check2:1542297108638335066>",
            )
            async def next_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                payment_embed = discord.Embed(
                    title="**<:card:1542297063331729529> Payment process**",
                    description=(
                        "This is an **automated system**; please **follow the instructions precisely** "
                        "and **avoid making any errors**. We remind you that we **do not offer refunds** "
                        "and are in no way **responsible** for any **errors** you might make.\n\n"
                        "To **pay your invoice**, please click the **button**: [<:card:1542297063331729529> **Complete your order**]\n\n"
                        "<:cart:1542297234404802570> **__Payment Information__ :**\n\n"
                        "**Invoice Total:**\n"
                        f"```{self.total_str} €```\n\n"
                        "**Payment Description (to be entered directly into PayPal):**\n"
                        f"```{self.payment_desc}```\n\n"
                        "<:info:1542297839026053190> If you encounter any **issues** with the **payment**, "
                        "or if our **automated system fails** to detect your **payment**, please **let us know**."
                    ),
                    color=discord.Color.from_str("#0058ff"),
                )

                if self.parent_view.bot_avatar:
                    payment_embed.set_footer(
                        text=self.parent_view.footer_text, icon_url=self.parent_view.bot_avatar
                    )
                else:
                    payment_embed.set_footer(text=self.parent_view.footer_text)

                class PayButtonView(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=None)
                        self.add_item(
                            discord.ui.Button(
                                label="Complete your order",
                                style=discord.ButtonStyle.link,
                                url="https://paypal.me/leazyttv",
                                emoji="<:card:1542297063331729529>",
                            )
                        )

                await interaction.response.edit_message(
                    embed=payment_embed, view=PayButtonView()
                )

        sent_msg = await target_chan.send(
            embed=final_embed,
            view=NextButtonView(self, total_str, payment_desc),
        )

        PENDING_INVOICES[payment_desc] = {
            "message_id": sent_msg.id,
            "channel_id": target_chan.id,
            "user_id": self.target_user.id,
            "total": float(total_str.replace(",", ".")),
            "footer_text": self.footer_text,
            "bot_avatar": self.bot_avatar,
        }

        await interaction.response.edit_message(
            content="✅ Invoice successfully sent!", embed=self.build_embed(), view=None
        )


class SendInvoiceButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Send Invoice",
            style=discord.ButtonStyle.secondary,
            emoji="<:check:1542297188498153513>",
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if not view.products:
            error_embed = discord.Embed(
                title="**<:info:1542297839026053190> Error**",
                description="There are **no products** added to the **invoice** yet.",
                color=discord.Color.from_str("#ff0000"),
            )
            if view.bot_avatar:
                error_embed.set_footer(
                    text=view.footer_text, icon_url=view.bot_avatar
                )
            else:
                error_embed.set_footer(text=view.footer_text)
            return await interaction.response.send_message(
                embed=error_embed, ephemeral=True
            )
        view.sending_mode = True
        view.refresh_components()
        await interaction.response.edit_message(view=view)


class BackMenuButton(discord.ui.Button):

    def __init__(self, parent_view=None):
        super().__init__(
            label="Back",
            style=discord.ButtonStyle.secondary,
            emoji="<:back:1542638431598022770>",
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        view.sending_mode = False
        view.mode = "main"
        view.refresh_components()
        await interaction.response.edit_message(view=view)


class InvoiceCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.web_runner = None
        self.bot.loop.create_task(self.start_web_server())

    async def start_web_server(self):
        app = web.Application()
        app.router.add_post('/ipn', self.handle_ipn)
        app.router.add_get('/', self.handle_index)
        
        runner = web.AppRunner(app)
        await runner.setup()
        port = int(os.environ.get("PORT", 10000))
        site = web.TCPSite(runner, '0.0.0.0', port)
        try:
            await site.start()
            print(f"[IPN Web Server] Running successfully on port {port}")
        except Exception as e:
            print(f"[IPN Web Server] Failed to start: {e}")

    async def handle_index(self, request):
        return web.Response(text="Receipt Tool Bot IPN Server is running!")

    async def handle_ipn(self, request):
        try:
            data = await request.json()
        except Exception:
            try:
                data = await request.post()
            except Exception:
                data = {}

        # Récupération sécurisée de la référence de facture
        payment_desc = (
            data.get("description") 
            or data.get("custom") 
            or data.get("item_name") 
            or data.get("payment_status")
        )
        
        if not payment_desc or payment_desc not in PENDING_INVOICES:
            return web.Response(status=404, text="Invoice not found or invalid description")

        invoice_info = PENDING_INVOICES[payment_desc]
        expected_total = invoice_info["total"]

        # Vérification du montant payé
        raw_gross = data.get("mc_gross") or data.get("payment_gross") or "0"
        try:
            paid_amount = float(str(raw_gross).replace(",", "."))
        except Exception:
            paid_amount = 0.0

        if paid_amount < expected_total:
            return web.Response(status=400, text=f"Insufficient amount: expected {expected_total}, got {paid_amount}")

        # Nettoyage de la facture en attente
        PENDING_INVOICES.pop(payment_desc)

        try:
            channel = self.bot.get_channel(invoice_info["channel_id"])
            if not channel:
                channel = await self.bot.fetch_channel(invoice_info["channel_id"])
            
            message = await channel.fetch_message(invoice_info["message_id"])
            
            completed_embed = discord.Embed(
                title="<:check:1542642100938477680> **Order successfully completed !**",
                description=(
                    "Thank you for **placing your trust** in us! Your **order** has been **paid for in full**. <:heart:1542642642964455484>\n\n"
                    "<:loading:1542642495480008794> We are **processing your order** as **quickly as possible** and will **keep you updated** on its progress.\n\n"
                    "<:question:1542297376755155044> If you have any **questions** or **specific additions** regarding your order, please **let us know here**."
                ),
                color=discord.Color.from_str("#0058ff"),
            )
            if invoice_info.get("bot_avatar"):
                completed_embed.set_footer(text=invoice_info["footer_text"], icon_url=invoice_info["bot_avatar"])
            else:
                completed_embed.set_footer(text=invoice_info["footer_text"])

            await message.edit(embed=completed_embed, view=None)
        except Exception as e:
            print(f"[IPN Error] Could not update Discord message: {e}")

        return web.Response(status=200, text="IPN processed successfully")

    @app_commands.command(
        name="invoice", description="Manage and create invoices."
    )
    @app_commands.describe(user="The discord user to create the invoice for")
    async def invoice(self, interaction: discord.Interaction, user: discord.User):
        bot_avatar = self.bot.user.display_avatar.url if self.bot.user else None
        bot_name = self.bot.user.name if self.bot.user else "Bot"
        now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
        footer_text = f"{bot_name} | {now_str}"

        user_role_ids = [role.id for role in interaction.user.roles]
        if ALLOWED_ROLE_ID not in user_role_ids:
            embed_refuse = discord.Embed(
                title="**<:info:1542297839026053190> Access denied**",
                description=(
                    "You do not have the required **permissions** to use"
                    " this **command**. This **action** is restricted to **staff**."
                ),
                color=discord.Color.from_str("#ff0000"),
            )
            if bot_avatar:
                embed_refuse.set_footer(text=footer_text, icon_url=bot_avatar)
            else:
                embed_refuse.set_footer(text=footer_text)
            return await interaction.response.send_message(
                embed=embed_refuse, ephemeral=True
            )

        view = InvoiceView(interaction, user, footer_text, bot_avatar)
        embed = view.build_embed()
        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(InvoiceCog(bot))