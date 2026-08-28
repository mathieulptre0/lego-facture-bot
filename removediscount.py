from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands

# Importation de la fonction depuis database.py
from database import remove_coupon_from_db

# Rôles autorisés (les mêmes que pour les autres commandes)
ALLOWED_ROLES = [
    1542206470970671214,
    1542219397534449877,
]


class RemoveDiscount(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="removediscount",
        description="Remove an existing discount coupon via its code.",
    )
    @app_commands.describe(
        code="The unique code of the coupon to remove",
    )
    async def removediscount(
        self,
        interaction: discord.Interaction,
        code: str,
    ):
        await interaction.response.defer(ephemeral=True)

        # Récupération de l'avatar et du nom du bot pour le footer
        bot_avatar = self.bot.user.display_avatar.url if self.bot.user else None
        bot_name = self.bot.user.name if self.bot.user else "Bot"
        now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
        footer_text = f"{bot_name} | {now_str}"

        # 1. Vérification des rôles autorisés
        user_role_ids = [role.id for role in interaction.user.roles]
        has_permission = any(role_id in ALLOWED_ROLES for role_id in user_role_ids)

        if not has_permission:
            embed_refuse = discord.Embed(
                title="<:info:1542297839026053190> Access denied",
                description=(
                    "You do not have the required **permissions** to **use**"
                    " this **command**. This **action** is **restricted** to **staff**."
                ),
                color=discord.Color.from_str("#0058ff"),
            )
            if bot_avatar:
                embed_refuse.set_footer(text=footer_text, icon_url=bot_avatar)
            else:
                embed_refuse.set_footer(text=footer_text)
            await interaction.followup.send(embed=embed_refuse, ephemeral=True)
            return

        # 2. Suppression du code dans la base de données MongoDB via database.py
        user_id, pourcentage = remove_coupon_from_db(code)

        if user_id is None:
            embed_not_found = discord.Embed(
                title="<:question:1542297376755155044> Code not found",
                description=(
                    f"No active coupon matches the code `{code.upper()}` in the"
                    " database."
                ),
                color=discord.Color.from_str("#0058ff"),
            )
            if bot_avatar:
                embed_not_found.set_footer(text=footer_text, icon_url=bot_avatar)
            else:
                embed_not_found.set_footer(text=footer_text)
            await interaction.followup.send(embed=embed_not_found, ephemeral=True)
            return

        utilisateur = interaction.guild.get_member(user_id) if user_id else None
        user_mention = utilisateur.mention if utilisateur else f"<@ID:{user_id}>"

        # 3. Réponse éphémère de succès pour l'administrateur
        embed_succes = discord.Embed(
            title=(
                "<:discount:1542297290411081778> Discount coupon deleted"
                " successfully."
            ),
            description=(
                "A discount coupon has just been deleted from the database by"
                f" {interaction.user.mention} :\n\n<:user:1542297519881592945>"
                f" **__Affected user__ :**"
                f" {user_mention}\n\n"
                f"<:code:1542297613787725945> **__Discount coupon__ :** `{code.upper()}`"
            ),
            color=discord.Color.from_str("#0058ff"),
        )
        if bot_avatar:
            embed_succes.set_footer(text=footer_text, icon_url=bot_avatar)
        else:
            embed_succes.set_footer(text=footer_text)

        await interaction.followup.send(embed=embed_succes, ephemeral=True)


async def setup(bot):
    await bot.add_cog(RemoveDiscount(bot))