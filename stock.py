import discord
from discord.ext import commands
from discord import app_commands

class StockProductModal(discord.ui.Modal, title="Product management"):
    product_name = discord.ui.TextInput(
        label="Product name",
        placeholder="Enter product name...",
        required=True
    )
    price = discord.ui.TextInput(
        label="Price",
        placeholder="Enter price...",
        required=True
    )
    quantity = discord.ui.TextInput(
        label="Quantity",
        placeholder="Enter quantity...",
        required=True
    )

    def __init__(self, view_instance, action_type):
        super().__init__()
        self.view_instance = view_instance
        self.action_type = action_type

    async def on_submit(self, interaction: discord.Interaction):
        name = self.product_name.value
        price = self.price.value
        qty = self.quantity.value

        if self.action_type == "add":
            self.view_instance.temp_products.append({"name": name, "price": price, "qty": qty})
        
        await self.view_instance.update_panel(interaction)

class StockSelect(discord.ui.Select):
    def __init__(self, view_instance):
        self.view_instance = view_instance
        options = [
            discord.SelectOption(label="Add a product from stock", description="Add a product", emoji="➕"),
            discord.SelectOption(label="Remove a product from stock", description="Remove a product", emoji="➖"),
            discord.SelectOption(label="Edit a product from stock", description="Edit a product", emoji="✏️")
        ]
        super().__init__(placeholder="Choose your option...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]
        if "Add" in val:
            await interaction.response.send_modal(StockProductModal(self.view_instance, "add"))
        elif "Remove" in val:
            if not self.view_instance.temp_products:
                await interaction.response.send_message("No products to remove.", ephemeral=True)
                return
            self.view_instance.temp_products.pop()
            await self.view_instance.update_panel(interaction)
        elif "Edit" in val:
            await interaction.response.send_message("Edit feature coming soon.", ephemeral=True)

class StockPanelView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.temp_products = []
        self.add_item(StockSelect(self))

    async def update_panel(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        
        desc = (
            "You can **create, edit, or delete** one or more products by clicking the **selection menu** located **below** this product.\n\n"
            "Once you have **made your selections**, please click the **\"Send\" button** to **update the message** in channel <#1543003779400732784>."
        )
        
        if self.temp_products:
            desc += "\n\n<:box:1542297038283079770> **__Future stock__ :**\n"
            desc += "<:cart:1542297234404802570> Products :     <:number:1543005258068918302> Number in stock :     <:euro:1542884660105715842> Price :\n"
            for p in self.temp_products:
                desc += f"{p['name']}     {p['qty']}     {p['price']} €\n"

        embed.description = desc
        if not interaction.response.is_done():
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Send", style=discord.ButtonStyle.primary, emoji="🚀", row=1)
    async def send_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.temp_products:
            await interaction.response.send_message("No products added to send.", ephemeral=True)
            return

        target_channel = interaction.guild.get_channel(1543003779400732784)
        if target_channel:
            public_embed = discord.Embed(
                title="<:stock:1543004710427041932> Stock",
                description=(
                    "Here is our **shop's current inventory**; the **stock updates automatically** whenever items become available !\n\n"
                    "<:box:1542297038283079770> **__Current stock__ :**\n"
                    "<:cart:1542297234404802570> Products :     <:number:1543005258068918302> Number in stock :     <:euro:1542884660105715842> Price :\n"
                ),
                color=0x0058ff
            )
            for p in self.temp_products:
                public_embed.description += f"{p['name']}     {p['qty']}     {p['price']} €\n"
            
            public_embed.description += f"\nIf you are **interested in purchasing** our products, please **open a ticket** at <#1542238377837989888> in the **Purchase category**."
            public_embed.set_footer(text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y à %H:%M')}")
            
            await target_channel.send(embed=public_embed)

        # Réinitialisation du panneau d'administration (suppression de la partie Future stock)
        self.temp_products = []
        embed = interaction.message.embeds[0]
        embed.description = (
            "You can **create, edit, or delete** one or more products by clicking the **selection menu** located **below** this product.\n\n"
            "Once you have **made your selections**, please click the **\"Send\" button** to **update the message** in channel <#1543003779400732784>."
        )
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send("Stock successfully updated and sent!", ephemeral=True)

class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stock", description="Affiche le panneau de gestion du stock")
    async def stock(self, interaction: discord.Interaction):
        role_id = 1542206470970671214
        if not any(role.id == role_id for role in interaction.user.roles):
            error_embed = discord.Embed(
                title="Erreur",
                description="Vous n'avez pas la permission d'utiliser cette commande.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        panel_channel = interaction.guild.get_channel(1543006150470008933)
        if not panel_channel:
            await interaction.response.send_message("Salon de panel introuvable.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Stock panel",
            description=(
                "You can **create, edit, or delete** one or more products by clicking the **selection menu** located **below** this product.\n\n"
                "Once you have **made your selections**, please click the **\"Send\" button** to **update the message** in channel <#1543003779400732784>."
            ),
            color=0x0058ff
        )
        embed.set_footer(text=f"Receipt Tool | {interaction.created_at.strftime('%d/%m/%Y à %H:%M')}")

        view = StockPanelView(self.bot)
        await panel_channel.send(embed=embed, view=view)
        await interaction.response.send_message("Le panneau de stock a bien été envoyé.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Stock(bot))