from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands

# Importation de la collection de coupons MongoDB
from database import coupons_collection

# Rôles autorisés (les mêmes que pour les autres commandes)
ALLOWED_ROLES = [
    1542206470970671214,
    1542219397534449877,
]


class DiscountList(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="discountlist",
        description="Display the list of all active discount coupons.",
    )
    async def discountlist(self, interaction: discord.Interaction):
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
            return await interaction.response.send_message(
                embed=embed_refuse, ephemeral=True
            )

        # 2. Récupération de tous les coupons depuis MongoDB
        all_coupons = list(coupons_collection.find({}))

        if not all_coupons:
            embed_empty = discord.Embed(
                title="<:discount:1542297290411081778> Active Discount Coupons",
                description=(
                    "There are currently **no active discount coupons** in the"
                    " database."
                ),
                color=discord.Color.from_str("#0058ff"),
            )
            if bot_avatar:
                embed_empty.set_footer(text=footer_text, icon_url=bot_avatar)
            else:
                embed_empty.set_footer(text=footer_text)
            return await interaction.response.send_message(
                embed=embed_empty, ephemeral=True
            )

        # 3. Création de l'embed principal
        embed_list = discord.Embed(
            title="<:discount:1542297290411081778> Active Discount Coupons List",
            description=(
                "Here is the **list** of **all active discount coupons** in the"
                " **database** :"
            ),
            color=discord.Color.from_str("#0058ff"),
        )

        users_col = []
        percentages_col = []
        codes_col = []

        for coupon in all_coupons:
            user_id = coupon.get("user_id")
            code = coupon.get("code", "N/A")
            pourcentage = coupon.get("Percentage", 0)

            utilisateur = interaction.guild.get_member(user_id) if user_id else None
            user_mention = utilisateur.mention if utilisateur else f"<@ID:{user_id}>"

            users_col.append(user_mention)
            percentages_col.append(f"`{pourcentage}%`")
            codes_col.append(f"`{code}`")

        # Ajout des colonnes sous forme de fields (inline=True)
        if users_col:
            embed_list.add_field(
                name="<:user:1542297519881592945> User",
                value="\n".join(users_col),
                inline=True,
            )
            embed_list.add_field(
                name="<:percent:1542297642405593228> Percentage",
                value="\n".join(percentages_col),
                inline=True,
            )
            embed_list.add_field(
                name="<:code:1542297613787725945> Coupons",
                value="\n".join(codes_col),
                inline=True,
            )

        if bot_avatar:
            embed_list.set_footer(text=footer_text, icon_url=bot_avatar)
        else:
            embed_list.set_footer(text=footer_text)

        await interaction.response.send_message(embed=embed_list, ephemeral=True)


async def setup(bot):
    await bot.add_cog(DiscountList(bot))