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
            self.view_instance.temp_products[self.product_index] = {"name": name, "price": price, "qty": qty}
        
        await self.view_instance.update_panel(interaction)

class RemoveProductSelect(discord.ui.Select):
    def __init__(self, view_instance):
        self.view_instance = view_instance
        options = []
        
        # On liste les produits déjà envoyés (ou en cours) pour les supprimer un par un
        products_source = self.view_instance.products if self.view_instance.products else self.view_instance.temp_products
        
        for index, p in enumerate(products_source):
            options.append(
                discord.SelectOption(
                    label=p['name'],
                    description=f"Price: {p['price']} € | Qty: {p['qty']}",
                    value=str(index)
                )
            )
        
        if not options:
            options.append(discord.SelectOption(label="No products available", value="none"))

        super().__init__(placeholder="Select a product to remove...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message("No products to remove.", ephemeral=True)
            return

        index = int(self.values[0])
        
        if self.view_instance.products:
            # Si on supprime depuis le stock actif, on supprime et on met à jour directement le salon public
            removed = self.view_instance.products.pop(index)
            await self.view_instance.sync_public_stock(interaction)
            await interaction.response.send_message(f"Product `{removed['name']}` removed from stock!", ephemeral=True)
        elif self.view_instance.temp_products:
            removed = self.view_instance.temp_products.pop(index)
            await interaction.response.send_message(f"Product `{removed['name']}` removed from temporary list.", ephemeral=True)
            
        await self.view_instance.update_panel(interaction)

class EditProductSelect(discord.ui.Select):
    def __init__(self, view_instance):
        self.view_instance = view_instance
        options = []
        products_source = self.view_instance.products if self.view_instance.products else self.view_instance.temp_products
        
        for index, p in enumerate(products_source):
            options.append(
                discord.SelectOption(
                    label=p['name'],
                    description=f"Price: {p['price']} € | Qty: {p['qty']}",
                    value=str(index)
                )
            )
        
        if not options:
            options.append(discord.SelectOption(label="No products available", value="none"))

        super().__init__(placeholder="Select a product to edit...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message("No products available to edit.", ephemeral=True)
            return

        index = int(self.values[0])
        products_source = self.view_instance.products if self.view_instance.products else self.view_instance.temp_products
        p = products_source[index]

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
        if "Add" in val:
            await interaction.response.send_modal(StockProductModal(self.view_instance, "add"))
        elif "Remove" in val:
            products_to_check = self.view_instance.products if self.view_instance.products else self.view_instance.temp_products
            if not products_to_check:
                await interaction.response.send_message("No products to remove.", ephemeral=True)
                return
            
            # Affiche un select secondaire pour choisir quel produit supprimer
            view = discord.ui.View()
            view.add_item(RemoveProductSelect(self.view_instance))
            await interaction.response.send_message("Select the product you want to remove:", view=view, ephemeral=True)

        elif "Edit" in val:
            products_to_check = self.view_instance.products if self.view_instance.products else self.view_instance.temp_products
            if not products_to_check:
                await interaction.response.send_message("No products to edit.", ephemeral=True)
                return
            
            # Affiche un select secondaire pour choisir quel produit modifier
            view = discord.ui.View()
            view.add_item(EditProductSelect(self.view_instance))
            await interaction.response.send_message("Select the product you want to edit:", view=view, ephemeral=True)

class StockPanelView(discord.ui.View):
    def __init__(self, bot, stock_message_id=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.temp_products = []
        self.products = []  # Produits validés et affichés dans le salon public
        self.stock_message_id = stock_message_id
        self.add_item(StockSelect(self))

    async def update_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Stock panel",
            description=(
                "You can **create, edit, or delete** one or more products by clicking the **selection menu** located **below** this product.\n\n"
                "Once you have **made your selections**, please click the **\"Send\" button** to **update the message** in channel <#1543003779400732784>."
            ),
            color=0x0058ff
        )
        
        display_products = self.temp_products if self.temp_products else self.products
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

    @discord.ui.button(label="Send", style=discord.ButtonStyle.secondary, emoji="<:check:1542297188498153513>", row=1)
    async def send_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.temp_products and not self.products:
            await interaction.response.send_message("No products added to send.", ephemeral=True)
            return

        if self.temp_products:
            self.products.extend(self.temp_products)
            self.temp_products = []

        await self.sync_public_stock(interaction)
        await self.update_panel(interaction)
        
        if not interaction.response.is_done():
            await interaction.response.send_message("Stock successfully updated and sent!", ephemeral=True)
        else:
            await interaction.followup.send("Stock successfully updated and sent!", ephemeral=True)

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