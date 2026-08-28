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
            if self.product_index < len(self.view_instance.temp_products):
                self.view_instance.temp_products[self.product_index] = {"name": name, "price": price, "qty": qty}
            else:
                real_index = self.product_index - len(self.view_instance.temp_products)
                self.view_instance.products[real_index] = {"name": name, "price": price, "qty": qty}
                await self.view_instance.sync_public_stock(interaction)
        
        self.view_instance.mode = "main"
        self.view_instance.rebuild_items()
        await self.view_instance.update_panel(interaction)

class StockProductSelect(discord.ui.Select):
    def __init__(self, view_instance, mode):
        self.view_instance = view_instance
        self.mode = mode
        options = []
        
        all_products = self.view_instance.temp_products + self.view_instance.products
        
        for index, p in enumerate(all_products):
            options.append(
                discord.SelectOption(
                    label=f"{p['name']}",
                    description=f"Price: {p['price']} € | Qty: {p['qty']}",
                    value=str(index),
                    emoji="<:arrow:1542297262544130168>"
                )
            )

        placeholder = "Select a product to remove..." if mode == "remove" else "Select a product to edit..."
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        index = int(self.values[0])
        all_products = self.view_instance.temp_products + self.view_instance.products
        p = all_products[index]

        if self.mode == "remove":
            if index < len(self.view_instance.temp_products):
                removed = self.view_instance.temp_products.pop(index)
                desc = f"Product `{removed['name']}` removed from temporary list."
            else:
                real_index = index - len(self.view_instance.temp_products)
                removed = self.view_instance.products.pop(real_index)
                await self.view_instance.sync_public_stock(interaction)
                desc = f"Product `{removed['name']}` removed from stock!"
            
            self.view_instance.mode = "main"
            self.view_instance.rebuild_items()
            await self.view_instance.update_panel(interaction)

            embed = discord.Embed(
                description=desc,
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

class BackToMenuButton(discord.ui.Button):
    def __init__(self, view_instance):
        self.view_instance = view_instance
        super().__init__(
            label="Back to menu",
            style=discord.ButtonStyle.secondary,
            emoji="<:back:1542638431598022770>",
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        self.view_instance.mode = "main"
        self.view_instance.rebuild_items()
        await self.view_instance.update_panel(interaction)

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
        total_products = len(self.view_instance.temp_products) + len(self.view_instance.products)

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
                text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y à %H:%M')}",
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
    def __init__(self, bot, stock_message_id=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.temp_products = []
        self.products = []
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
            self.add_item(BackToMenuButton(self))

    async def update_panel(self, interaction: discord.Interaction):
        mode_text = "remove product" if self.mode == "remove" else "edit product" if self.mode == "edit" else ""
        
        if self.mode != "main":
            description = f"You are **currently** on the **{mode_text} page** ! ✨\n\nSelect a product from the **selection menu** below to **{self.mode}** it."
        else:
            description = (
                "You can **create, edit, or delete** one or more products by clicking the **selection menu** located **below** this product.\n\n"
                "Once you have **made your selections**, please click the **\"Send\" button** to **update the message** in channel <#1543003779400732784>."
            )

        embed = discord.Embed(
            title="Stock panel",
            description=description,
            color=0x0058ff
        )
        
        display_products = self.temp_products if self.temp_products else self.products
        if self.mode == "main" and display_products:
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
            text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y à %H:%M')}",
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
                "<:box:1542297038283079770> **__Current stock__ :**"
            ),
            color=0x0058ff
        )
        
        if self.products:
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
            text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y à %H:%M')}",
            icon_url=self.bot.user.display_avatar.url
        )
        
        if self.stock_message_id:
            try:
                existing_msg = await target_channel.fetch_message(self.stock_message_id)
                await existing_msg.edit(embed=public_embed)
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
        if not self.view_instance.temp_products and not self.view_instance.products:
            error_embed = discord.Embed(
                title="<:info:1542297188498153513> Error",
                description="There are **no products** added to the **invoice** yet.",
                color=discord.Color.red()
            )
            error_embed.set_footer(
                text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y à %H:%M')}",
                icon_url=interaction.client.user.display_avatar.url
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

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
            text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y à %H:%M')}",
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
            text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y à %H:%M')}",
            icon_url=self.bot.user.display_avatar.url
        )

        view = StockPanelView(self.bot, stock_message_id=stock_msg.id)
        await panel_channel.send(embed=panel_embed, view=view)
        
        await interaction.response.send_message("Stock and panel embeds have been successfully initialized.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Stock(bot))