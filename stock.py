import discord
from discord.ext import commands
from discord import app_commands

class StockProductModal(discord.ui.Modal):
    def __init__(self, view_instance, action_type, product_index=None, current_name="", current_price="", current_qty=""):
        self.view_instance = view_instance
        self.action_type = action_type
        self.product_index = product_index
        
        title = "Edit product" if action_type == "edit" else "Product management"
        super().__init__(title=title)

        self.product_name = discord.ui.TextInput(
            label="Product name",
            placeholder="Enter product name...",
            default=current_name,
            required=True
        )
        self.price = discord.ui.TextInput(
            label="Price",
            placeholder="Enter price...",
            default=str(current_price),
            required=True
        )
        self.quantity = discord.ui.TextInput(
            label="Quantity",
            placeholder="Enter quantity...",
            default=str(current_qty),
            required=True
        )

        self.add_item(self.product_name)
        self.add_item(self.price)
        self.add_item(self.quantity)

    async def on_submit(self, interaction: discord.Interaction):
        name = self.product_name.value
        price = self.price.value
        qty = self.quantity.value

        if self.action_type == "add":
            self.view_instance.temp_products.append({"name": name, "price": price, "qty": qty})
        elif self.action_type == "edit" and self.product_index is not None:
            self.view_instance.pending_edits[self.product_index] = {"name": name, "price": price, "qty": qty}
        
        self.view_instance.mode = "main"
        self.view_instance.rebuild_items()
        await self.view_instance.update_panel(interaction)

class StockProductSelect(discord.ui.Select):
    def __init__(self, view_instance, mode):
        self.view_instance = view_instance
        self.mode = mode
        options = []
        
        all_products = self.view_instance.products
        
        for index, p in enumerate(all_products):
            if mode == "remove" and index in self.view_instance.pending_removes:
                continue
            
            current_p = self.view_instance.pending_edits.get(index, p)
            
            options.append(
                discord.SelectOption(
                    label=f"{current_p['name']}",
                    description=f"Price: {current_p['price']} € | Qty: {current_p['qty']}",
                    value=str(index),
                    emoji="<:arrow:1542297262544130168>"
                )
            )

        options.append(
            discord.SelectOption(
                label="Back to menu",
                emoji="<:back:1542638431598022770>",
                value="back_to_menu"
            )
        )

        placeholder = "Select a product to remove..." if mode == "remove" else "Select a product to edit..."
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "back_to_menu":
            self.view_instance.mode = "main"
            self.view_instance.rebuild_items()
            await self.view_instance.update_panel(interaction)
            await interaction.response.defer()
            return

        index = int(self.values[0])
        all_products = self.view_instance.products
        p = self.view_instance.pending_edits.get(index, all_products[index])

        if self.mode == "remove":
            if index not in self.view_instance.pending_removes:
                self.view_instance.pending_removes.append(index)
            
            self.view_instance.rebuild_items()
            await self.view_instance.update_panel(interaction)

            embed = discord.Embed(
                description=f"Product `{p['name']}` marked for removal in the panel. Click **Send** to apply changes to the stock channel.",
                color=0x0058ff
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif self.mode == "edit":
            await interaction.response.send_modal(
                StockProductModal(
                    self.view_instance, 
                    action_type="edit", 
                    product_index=index, 
                    current_name=p['name'], 
                    current_price=p['price'], 
                    current_qty=p['qty']
                )
            )

class StockSelect(discord.ui.Select):
    def __init__(self, view_instance):
        self.view_instance = view_instance
        options = [
            discord.SelectOption(label="Add a product from stock", description="Add a product", emoji="<:add:1542564459925741608>"),
            discord.SelectOption(label="Remove a product from stock", description="Remove a product", emoji="<:remove:1542564590074855525>"),
            discord.SelectOption(label="Edit a product from stock", description="Edit a product", emoji="<:edit:1542564664192409631>")
        ]
        super().__init__(placeholder="Choose your option...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]
        total_products = len(self.view_instance.products)

        if "Add" in val:
            await interaction.response.send_modal(StockProductModal(self.view_instance, "add"))
            return

        if total_products == 0:
            error_embed = discord.Embed(
                title="<:info:1542297188498153513> Error",
                description="There are **no products** added to the **stock** yet.",
                color=discord.Color.red()
            )
            error_embed.set_footer(
                text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y at %H:%M')}",
                icon_url=interaction.client.user.display_avatar.url
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        if "Remove" in val:
            self.view_instance.mode = "remove"
        elif "Edit" in val:
            self.view_instance.mode = "edit"

        self.view_instance.rebuild_items()
        await self.view_instance.update_panel(interaction)
        await interaction.response.defer()

class StockPanelView(discord.ui.View):
    def __init__(self, bot, stock_message_id=None, initial_products=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.products = initial_products if initial_products else []
        self.temp_products = []
        self.pending_removes = []
        self.pending_edits = {}
        self.stock_message_id = stock_message_id
        self.mode = "main"
        self.rebuild_items()

    def rebuild_items(self):
        self.clear_items()
        if self.mode == "main":
            self.add_item(StockSelect(self))
            self.add_item(SendButton(self))
        else:
            self.add_item(StockProductSelect(self, self.mode))
            self.add_item(SendButton(self))

    def get_preview_products(self):
        simulated = [dict(p) for p in self.products]
        
        for idx, new_data in self.pending_edits.items():
            if idx < len(simulated):
                simulated[idx] = new_data

        simulated.extend(self.temp_products)

        for idx in sorted(self.pending_removes, reverse=True):
            if idx < len(simulated):
                simulated.pop(idx)

        return simulated

    async def update_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Stock panel",
            description=(
                "You can **create, edit, or delete** one or more products by clicking the **selection menu** located **below** this product.\n\n"
                "Once you have **made your selections**, please click the **\"Send\" button** to **update the message** in channel <#1543003779400732784>."
            ),
            color=0x0058ff
        )
        
        display_products = self.get_preview_products()
        if display_products:
            embed.add_field(
                name="\u200b",
                value="<:box:1542297038283079770> **__Products__ :**",
                inline=False
            )
            names = [f"`{p['name']}`" for p in display_products]
            prices = [f"`{p['price']} €`" for p in display_products]
            qtys = [f"`{p['qty']}`" for p in display_products]

            embed.add_field(name="<:cart:1542297234404802570> Product", value="\n".join(names), inline=True)
            embed.add_field(name="<:euro:1542884660105715842> Price", value="\n".join(prices), inline=True)
            embed.add_field(name="<:number:1543005258068918302> Quantity", value="\n".join(qtys), inline=True)

        embed.set_footer(
            text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y at %H:%M')}",
            icon_url=self.bot.user.display_avatar.url
        )

        if interaction.response.is_done():
            try:
                await interaction.message.edit(embed=embed, view=self)
            except Exception:
                pass
        else:
            await interaction.response.edit_message(embed=embed, view=self)

    async def sync_public_stock(self, interaction: discord.Interaction):
        target_channel = interaction.guild.get_channel(1543003779400732784)
        if not target_channel:
            return

        public_embed = discord.Embed(
            title="<:stock:1543004710427041932> Stock",
            description=(
                "Here is our **shop's current inventory**; the **stock updates automatically** whenever items become available !\n\n"
                "If you are **interested in purchasing** our products, please **open a ticket** at <#1542238377837989888> in the **Purchase category**."
            ),
            color=0x0058ff
        )
        
        if self.products:
            public_embed.description = (
                "Here is our **shop's current inventory**; the **stock updates automatically** whenever items become available !\n\n"
                "<:box:1542297038283079770> **__Current stock__ :**"
            )
            names = [f"`{p['name']}`" for p in self.products]
            prices = [f"`{p['price']} €`" for p in self.products]
            qtys = [f"`{p['qty']}`" for p in self.products]

            public_embed.add_field(name="<:cart:1542297234404802570> Product", value="\n".join(names), inline=True)
            public_embed.add_field(name="<:euro:1542884660105715842> Price", value="\n".join(prices), inline=True)
            public_embed.add_field(name="<:number:1543005258068918302> Quantity", value="\n".join(qtys), inline=True)
            
            public_embed.add_field(
                name="\u200b",
                value=f"If you are **interested in purchasing** our products, please **open a ticket** at <#1542238377837989888> in the **Purchase category**.",
                inline=False
            )

        public_embed.set_footer(
            text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y at %H:%M')}",
            icon_url=interaction.client.user.display_avatar.url
        )
        
        if self.stock_message_id:
            try:
                existing_msg = await target_channel.fetch_message(self.stock_message_id)
                await existing_msg.edit(embed=public_embed, view=None)
                return
            except discord.NotFound:
                pass

        new_msg = await target_channel.send(embed=public_embed)
        self.stock_message_id = new_msg.id

class SendButton(discord.ui.Button):
    def __init__(self, view_instance):
        self.view_instance = view_instance
        super().__init__(
            label="Send",
            style=discord.ButtonStyle.secondary,
            emoji="<:check:1542297188498153513>",
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        for idx, new_data in self.view_instance.pending_edits.items():
            if idx < len(self.view_instance.products):
                self.view_instance.products[idx] = new_data

        for idx in sorted(self.view_instance.pending_removes, reverse=True):
            if idx < len(self.view_instance.products):
                self.view_instance.products.pop(idx)

        self.view_instance.pending_removes.clear()
        self.view_instance.pending_edits.clear()

        if self.view_instance.temp_products:
            self.view_instance.products.extend(self.view_instance.temp_products)
            self.view_instance.temp_products = []

        self.view_instance.mode = "main"
        self.view_instance.rebuild_items()

        await self.view_instance.sync_public_stock(interaction)
        await self.view_instance.update_panel(interaction)
        
        success_embed = discord.Embed(
            description="Stock successfully updated and sent!",
            color=0x0058ff
        )
        if not interaction.response.is_done():
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        else:
            await interaction.followup.send(embed=success_embed, ephemeral=True)

class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stock", description="Displays the stock management panel and inventory")
    async def stock(self, interaction: discord.Interaction):
        role_id = 1542206470970671214
        if not any(role.id == role_id for role in interaction.user.roles):
            error_embed = discord.Embed(
                title="Error",
                description="You do not have the required permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        panel_channel = interaction.guild.get_channel(1543006150470008933)
        stock_channel = interaction.guild.get_channel(1543003779400732784)
        
        if not panel_channel or not stock_channel:
            await interaction.response.send_message("One of the required channels could not be found.", ephemeral=True)
            return

        public_embed = discord.Embed(
            title="<:stock:1543004710427041932> Stock",
            description=(
                "Here is our **shop's current inventory**; the **stock updates automatically** whenever items become available !\n\n"
                "If you are **interested in purchasing** our products, please **open a ticket** at <#1542238377837989888> in the **Purchase category**."
            ),
            color=0x0058ff
        )
        public_embed.set_footer(
            text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y at %H:%M')}",
            icon_url=self.bot.user.display_avatar.url
        )
        stock_msg = await stock_channel.send(embed=public_embed)

        panel_embed = discord.Embed(
            title="Stock panel",
            description=(
                "You can **create, edit, or delete** one or more products by clicking the **selection menu** located **below** this product.\n\n"
                "Once you have **made your selections**, please click the **\"Send\" button** to **update the message** in channel <#1543003779400732784>."
            ),
            color=0x0058ff
        )
        panel_embed.set_footer(
            text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y at %H:%M')}",
            icon_url=self.bot.user.display_avatar.url
        )

        view = StockPanelView(self.bot, stock_message_id=stock_msg.id)
        await panel_channel.send(embed=panel_embed, view=view)
        
        await interaction.response.send_message("Stock and panel embeds have been successfully initialized.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Stock(bot))