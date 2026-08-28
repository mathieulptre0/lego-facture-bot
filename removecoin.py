from datetime import datetime
import json
import os
subprocess = __import__("subprocess")
import discord
from discord import app_commands
from discord.ext import commands

# Chemin sécurisé pour cibler le JSON dans le dossier bot discord
DB_FILE = os.path.join(os.path.dirname(__file__), "coins_db.json")

# Nouveaux rôles autorisés uniquement
ALLOWED_ROLES = [
    1542206470970671214,
    1542219397534449877,
]


def load_database():
  if not os.path.exists(DB_FILE):
    return {}
  with open(DB_FILE, "r", encoding="utf-8") as f:
    try:
      return json.load(f)
    except json.JSONDecodeError:
      return {}


def save_database(data):
  with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
  
  # Sauvegarde persistante pour éviter la perte sur les hébergeurs cloud éphémères
  try:
    subprocess.run(["git", "config", "--global", "user.name", "Bot Coins"], check=False)
    subprocess.run(["git", "config", "--global", "user.email", "bot@local.com"], check=False)
    subprocess.run(["git", "add", DB_FILE], check=False)
    subprocess.run(["git", "commit", "-m", "Auto-save coins database (remove)"], check=False)
    subprocess.run(["git", "push"], check=False)
  except Exception as e:
    print(f"Erreur lors de la synchronisation Git automatique : {e}")


def update_user_coins(user_id: int, amount: int):
  db = load_database()
  str_user_id = str(user_id)
  if str_user_id not in db:
    db[str_user_id] = {"coins": 0}
  
  # Soustraction des coins tout en s'assurant de ne pas descendre en dessous de 0
  current = db[str_user_id].get("coins", 0)
  db[str_user_id]["coins"] = max(0, current - amount)
  
  new_total = db[str_user_id]["coins"]
  save_database(db)
  return new_total


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

    nouveau_total = update_user_coins(user.id, number)

    embed_succes = discord.Embed(
        title="<:check2:1542297108638335066> Coins removal successful",
        description=(
            "The **coins** have been **successfully removed** from the **profile** of"
            f" the **user**.\n\n<:user:1542297519881592945>"
            f" __**Affected user**__ : {user.mention}\n\n<:coin:1542297155660812348>"
            f" __**Removed coins**__ : `{number}`\n\n<:wallet:1542297543063507034>"
            f" __**New user personal balance**__ : `{nouveau_total} coins`"
        ),
        color=discord.Color.from_str("#ff0000"),
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
              f" `{number}`\n\n<:wallet:1542297543063507034>"
              f" __**New personal balance**__ : `{nouveau_total} coins`"
          ),
          color=discord.Color.from_str("#ff0000"),
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