from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands

# Importation de nos fonctions MongoDB centralisées
from database import coins_collection

# Nouveaux rôles autorisés uniquement
ALLOWED_ROLES = [
    1542206470970671214,
    1542219397534449877,
]

def update_user_coins(user_id: int, amount: int):
    # Recherche l'utilisateur dans MongoDB, s'il n'existe pas on initialise à 0
    user_data = coins_collection.find_one({"user_id": user_id})
    current_coins = user_data["coins"] if user_data else 0
    new_total = current_coins + amount

    # Met à jour ou insère directement dans la base de données en ligne
    coins_collection.update_one(
        {"user_id": user_id},
        {"$set": {"coins": new_total}},
        upsert=True
    )
    return new_total


class AddCoin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="addcoin", description="Add coins to a user"
    )
    @app_commands.describe(
        user="The user to whom coins are to be added",
        number="The number of coins to add",
    )
    async def addcoin(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        number: int,
    ):
        bot_avatar = self.bot.user.display_avatar.url if self.bot.user else None
        bot_name = self.bot.user.name if self.bot.user else "Bot"
        now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
        footer_text = f"{bot_name} | {now_str}"

        user_role_ids = [role.id for role in interaction.user.roles]
        has_permission = any(role_id in ALLOWED_ROLES for role_id in user_role_ids)

        if not has_permission:
            embed_refuse = discord.Embed(
                title="<:info:1542297839026053190> Access denied Accès refusé",
                description=(
                    "You do not have the required **permissions** to **use**"
                    " this **command**. This **action** is **restricted** to **staff**."
                    " allowed."
                ),
                color=discord.Color.from_str("#ff0000"),
            )
            if bot_avatar:
                embed_refuse.set_footer(text=footer_text, icon_url=bot_avatar)
            else:
                embed_refuse.set_footer(text=footer_text)
            await interaction.response.send_message(embed=embed_refuse, ephemeral=True)
            return

        nouveau_total = update_user_coins(user.id, number)

        embed_succes = discord.Embed(
            title="<:check2:1542297108638335066> Coins addition successful",
            description=(
                "The **coins** have been **successfully added** to the **profile** of"
                f" the **user**.\n\n<:user:1542297519881592945>"
                f" __**Affected user**__ : {user.mention}\n\n<:coin:1542297155660812348>"
                f" __**Added coins**__ : `{number}`\n\n<:wallet:1542297543063507034>"
                f" __**New user personal balance**__ : `{nouveau_total} coins`"
            ),
            color=discord.Color.from_str("#0058ff"),
        )
        if bot_avatar:
            embed_succes.set_footer(text=footer_text, icon_url=bot_avatar)
        else:
            embed_succes.set_footer(text=footer_text)

        await interaction.response.send_message(embed=embed_succes, ephemeral=True)

        try:
            embed_dm = discord.Embed(
                title="<:bank:1542297721375957042> Updating your coin balance",
                description=(
                    "An **administrator** has just **credited** your **account** with"
                    f" **coins** !\n\n<:coin:1542297155660812348> __**Coins added**__ :"
                    f" `{number}`\n\n<:wallet:1542297543063507034>"
                    f" __**New personal balance**__ : `{nouveau_total} coins`"
                ),
                color=discord.Color.from_str("#0058ff"),
            )
            if bot_avatar:
                embed_dm.set_footer(text=footer_text, icon_url=bot_avatar)
            else:
                embed_dm.set_footer(text=footer_text)
            await user.send(embed=embed_dm)
        except discord.HTTPException:
            pass


async def setup(bot):
    await bot.add_cog(AddCoin(bot))