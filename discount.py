from datetime import datetime
import random
import string
import discord
from discord import app_commands
from discord.ext import commands

# Importation de notre fonction depuis database.py
from database import save_user_coupon

# Rôles autorisés (les mêmes que pour les coins)
ALLOWED_ROLES = [
    1542206470970671214,
    1542219397534449877,
]


def generate_coupon_code():
    """Generates a code in the format LZGO-XXXX-XXXX-XXXX."""

    def random_part(length=4):
        chars = string.ascii_uppercase + string.digits
        return "".join(random.choices(chars, k=length))

    return f"LZGO-{random_part()}-{random_part()}-{random_part()}"


class Discount(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="discount",
        description="Create and send a discount coupon to a user.",
    )
    @app_commands.describe(
        user="The user to whom the coupon should be sent",
        percentage="The discount percentage (e.g., 20)",
    )
    async def discount(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        percentage: int,
    ):
        # Récupération de l'avatar et du nom du bot pour le footer
        bot_avatar = self.bot.user.display_avatar.url if self.bot.user else None
        bot_name = self.bot.user.name if self.bot.user else "Bot"
        now_str = datetime.now().strftime("%d/%m/%Y at %H:%M")
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
            await interaction.response.send_message(embed=embed_refuse, ephemeral=True)
            return

        # 2. Génération du code et sauvegarde dans MongoDB via database.py
        code_unique = generate_coupon_code()
        save_user_coupon(user.id, code_unique, percentage)

        # 3. Réponse éphémère de succès pour l'administrateur
        embed_succes = discord.Embed(
            title=(
                "<:discount:1542297290411081778> Discount coupon created and sent"
                " successfully."
            ),
            description=(
                "A new discount coupon has just been created/sent from the"
                f" share of {interaction.user.mention} :\n\n<:user:1542297519881592945>"
                f" **__Affected user__ :**"
                f" {user.mention}\n\n<:percent:1542297642405593228>"
                f" **__Percentage applied__ :**"
                f" `{percentage}%`\n\n<:code:1542297613787725945>"
                f" **__Discount coupon__ :** `{code_unique}`"
            ),
            color=discord.Color.from_str("#0058ff"),
        )
        if bot_avatar:
            embed_succes.set_footer(text=footer_text, icon_url=bot_avatar)
        else:
            embed_succes.set_footer(text=footer_text)

        await interaction.response.send_message(embed=embed_succes, ephemeral=True)

        # 4. Envoi du message privé (DM) à l'utilisateur ciblé
        try:
            embed_dm = discord.Embed(
                title=(
                    "<:discount:1542297290411081778> Discount coupon"
                ),
                description=(
                    "You have just received an **exclusive discount coupon** ! <:party:1542297685170851840>\n\n"
                    "## <:guide:1542297329200144414> **__Details of your offer__"
                    " :**\n\n<:code:1542297613787725945> **__Unique code__ :**\n"
                    f" ```{code_unique}```\n\n<:percent:1542297642405593228>"
                    f" **__Discount value__ :**"
                    f" `{percentage}%`\n\n## <:cart:1542297234404802570> How"
                    " use it?\n\n1.) Head over to our **Discord server**"
                    " in the **dedicated lounge** : <#1542238377837989888>.\n\n2.)"
                    " **Place** your order.\n\n3.) Submit your"
                    " **unique code** to **immediately** apply your"
                    " **reduction**.\n\nThis **code** is **strictly personal**."
                    " **Make the most of it** !"
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
    await bot.add_cog(Discount(bot))