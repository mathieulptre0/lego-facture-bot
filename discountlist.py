from datetime import datetime
import json
import os
import discord
from discord import app_commands
from discord.ext import commands

# Chemin sécurisé pour stocker les coupons dans le dossier bot discord
DB_FILE = os.path.join(os.path.dirname(__file__), "coupons_db.json")

# Rôles autorisés (les mêmes que pour les autres commandes)
ALLOWED_ROLES = [
    1542206470970671214,
    1542219397534449877,
]


def load_database():
  """Loads the coupon database."""
  if not os.path.exists(DB_FILE):
    return {}
  with open(DB_FILE, "r", encoding="utf-8") as f:
    try:
      return json.load(f)
    except json.JSONDecodeError:
      return {}


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
              " allowed."
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

    # 2. Chargement des données de la base de données
    db = load_database()

    if not db:
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

    # 3. Création de l'embed principal avec les mots importants en gras
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

    for str_user_id, coupons in db.items():
      utilisateur = interaction.guild.get_member(int(str_user_id))
      user_mention = utilisateur.mention if utilisateur else f"<@ID:{str_user_id}>"

      if isinstance(coupons, list):
        for coupon in coupons:
          code = coupon.get("code", "N/A")
          pourcentage = coupon.get("Percentage", 0)

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