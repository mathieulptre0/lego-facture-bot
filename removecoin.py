from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands

# Importation de la fonction depuis database.py
from database import update_user_coins

# Nouveaux rôles autorisés uniquement
ALLOWED_ROLES = [
    1542206470970671214,
    1542219397534449877,
]


class RemoveCoin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="removecoin", description="Remove coins from a user"
    )
    @app_commands.describe(
        user="The user from whom coins are to be removed",
        number="The number of coins to remove",
    )
    async def removecoin(
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
                ),
                color=discord.Color.from_str("#ff0000"),
            )
            if bot_avatar:
                embed_refuse.set_footer(text=footer_text, icon_url=bot_avatar)
            else:
                embed_refuse.set_footer(text=footer_text)
            await interaction.response.send_message(embed=embed_refuse, ephemeral=True)
            return

        if number <= 0:
            error_embed = discord.Embed(
                title="<:info:1542297839026053190> Error",
                description="You must remove at least **1 coin**.",
                color=discord.Color.from_str("#ff0000"),
            )
            if bot_avatar:
                error_embed.set_footer(text=footer_text, icon_url=bot_avatar)
            else:
                error_embed.set_footer(text=footer_text)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)

        # Récupérer d'abord le solde actuel de l'utilisateur (si la fonction existe dans database.py, sinon on ajuste via update)
        # On tente de récupérer le solde actuel ou on applique directement la logique sécurisée :
        # On retire les coins, et si le nouveau total est < 0, on remet à 0 et on calcule combien ont été réellement retirés.
        
        # Astuce : On récupère le solde avant modification si ta bdd le permet, ou on gère via le retour de update_user_coins
        nouveau_total = update_user_coins(user.id, -number)
        
        removed_actual = number
        if nouveau_total < 0:
            # Calcul de la quantité exacte qui a pu être retirée pour atteindre 0
            removed_actual = number + nouveau_total  # ex: 9 - 10 = -1 -> 10 + (-1) = 9 retirés
            nouveau_total = update_user_coins(user.id, -nouveau_total) # Remet le solde exactement à 0

        embed_succes = discord.Embed(
            title="<:check2:1542297108638335066> Coins removal successful",
            description=(
                "The **coins** have been **successfully removed** from the **profile** of"
                f" the **user**.\n\n<:user:1542297519881592945>"
                f" __**Affected user**__ : {user.mention}\n\n<:coin:1542297155660812348>"
                f" __**Removed coins**__ : `{removed_actual}`\n\n<:wallet:1542297543063507034>"
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
                    "An **administrator** has just **removed** **coins** from your **account**"
                    f" !\n\n<:coin:1542297155660812348> __**Coins removed**__ :"
                    f" `{removed_actual}`\n\n<:wallet:1542297543063507034>"
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
    await bot.add_cog(RemoveCoin(bot))