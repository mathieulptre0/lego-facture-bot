from datetime import datetime
import json
import os
import discord
from discord import app_commands
from discord.ext import commands

# Importation de la fonction de génération du PDF depuis le fichier receipt.py
from receipt import executer_generation_complete

# Chemin de la base de données des coins
DB_FILE = os.path.join(os.path.dirname(__file__), "coins_db.json")

# ID du rôle requis pour exécuter la commande /receipt
REQUIRED_ROLE_ID = 1542206470970671214

# ID du salon où envoyer l'embed de configuration du système
RECEIPT_CHANNEL_ID = 1542876927201644595


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


def get_user_coins(user_id: int) -> int:
  db = load_database()
  return db.get(str(user_id), {}).get("coins", 0)


def remove_user_coin(user_id: int, amount: int = 1):
  db = load_database()
  str_user_id = str(user_id)
  if str_user_id not in db:
    db[str_user_id] = {"coins": 0}
  db[str_user_id]["coins"] = max(0, db[str_user_id]["coins"] - amount)
  save_database(db)


class ReceiptModal(discord.ui.Modal, title="Receipt Creation"):
  item_name = discord.ui.TextInput(
      label="Item name",
      placeholder="Entrez le nom de l'article...",
      required=True,
      max_length=100,
  )
  item_price = discord.ui.TextInput(
      label="Item price",
      placeholder="Ex: 5.99 ou 1",
      required=True,
      max_length=20,
  )
  purchase_date = discord.ui.TextInput(
      label="Date of purchase / time",
      placeholder="JJ/MM/AAAA HH:MM:SS (ex: 24/08/2026 19:35:15)",
      required=True,
      max_length=30,
  )

  async def on_submit(self, interaction: discord.Interaction):
    user_id = interaction.user.id
    bot_avatar = self.bot_ref.user.display_avatar.url if self.bot_ref.user else None
    bot_name = self.bot_ref.user.name if self.bot_ref.user else "Bot"
    now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    footer_text = f"{bot_name} | {now_str}"

    # Vérification du solde de coins
    current_coins = get_user_coins(user_id)
    if current_coins < 1:
      embed_err = discord.Embed(
          title="<:info:1542297839026053190> Insufficient Balance",
          description=(
              "You **do not have enough coins** in your account to **create a receipt**.\n\n"
              "Please **open a ticket** at <#1542238377837989888> to **order some**!"
          ),
          color=discord.Color.from_str("#ff0000"),
      )
      if bot_avatar:
        embed_err.set_footer(text=footer_text, icon_url=bot_avatar)
      else:
        embed_err.set_footer(text=footer_text)
      await interaction.response.send_message(embed=embed_err, ephemeral=True)
      return

    # Retrait d'un coin
    remove_user_coin(user_id, 1)

    # Récupération et formatage des données du formulaire
    raw_name = self.item_name.value.strip()
    raw_price = self.item_price.value.strip().replace(",", ".")
    raw_date = self.purchase_date.value.strip()

    try:
      price_float = float(raw_price)
      price_str = f"{price_float:.2f}".replace(".", ",") + " €"
    except ValueError:
      price_float = 5.99
      price_str = "5,99 €"

    # Calcul de la TVA à 20%
    tva_float = price_float * 0.20
    tva_str = f"{tva_float:.2f}".replace(".", ",") + " €"

    # Parsing de la date et l'heure pour adapter le reçu
    try:
      dt_obj = datetime.strptime(raw_date, "%d/%m/%Y %H:%M:%S")
    except ValueError:
      try:
        dt_obj = datetime.strptime(raw_date, "%d/%m/%Y %H:%M")
      except ValueError:
        dt_obj = datetime.now()

    formatted_date_slash = dt_obj.strftime("%d/%m/%Y %H:%M:%S")
    formatted_time = dt_obj.strftime("%H:%M:%S")

    months_fr = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril",
        5: "mai", 6: "juin", 7: "juillet", 8: "août",
        9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
    }
    formatted_date_written = f"{dt_obj.day} {months_fr[dt_obj.month]} {dt_obj.year}"

    # Code d'avis dynamique basé sur la date (ex: 149-64863689-MM-JJ-AAAA)
    code_besoin_str = f"149-64863689-{dt_obj.strftime('%m-%d-%Y')} "

    # Modification dynamique du fichier receipt.py / variables globales si besoin,
    # ou exécution directe en surchargeant les variables du module receipt.
    import receipt as receipt_mod
    
    # Injection des variables dans le module receipt avant génération
    receipt_mod.texte_article = raw_name
    receipt_mod.texte_p1 = price_str
    receipt_mod.texte_1e_nouveau = tva_str
    receipt_mod.texte_1e = tva_str
    receipt_mod.texte_tot_payer = price_str
    receipt_mod.texte_599e = price_str
    receipt_mod.texte_code_besoin = code_besoin_str
    receipt_mod.texte_date_valeur = formatted_date_slash
    receipt_mod.texte_date_val = formatted_date_written
    receipt_mod.texte_heure_val = formatted_time

    # Génération du PDF
    try:
      executer_generation_complete()
    except Exception as e:
      print(f"Erreur lors de la génération du PDF : {e}")

    pdf_path = os.path.join(r"C:\Users\leazy\Desktop\lego facture bot", "Receipt.py" if False else "Receipt.pdf")

    # Création de l'embed de succès éphémère
    embed_success = discord.Embed(
        title="<:check:1542642100938477680> Receipt successfully created !",
        description=(
            "We have **finished creating** your invoice.\n\n"
            "<:edit:1542564664192409631> **__Updated information__:**\n\n"
            "<:name:1542884240985948240> **Item name:** ```" + raw_name + "```\n"
            "<:euro:1542884660105715842> **Item price:** ```" + price_str + "```\n"
            "<:date:1542886387358105681> **Purchase date:** ```" + formatted_date_slash + "```"
        ),
        color=discord.Color.from_str("#0058ff"),
    )
    if bot_avatar:
      embed_success.set_footer(text=footer_text, icon_url=bot_avatar)
    else:
      embed_success.set_footer(text=footer_text)

    view = discord.ui.View()
    if os.path.exists(pdf_path):
      file_to_send = discord.File(pdf_path, filename="Receipt.pdf")
      view.add_item(discord.ui.Button(
          style=discord.ButtonStyle.secondary,
          label="Download the receipt",
          emoji="<:download:1542886821279563918>",
          url="https://discord.com" # Remplace par un lien ou envoie le fichier directement via discord si attachment
      ))
      # Note: Discord ne permet pas de lier un lien URL cliquable direct vers un fichier local via un bouton URL standard,
      # on envoie donc le fichier en pièce jointe ou via un canal sécurisé si besoin.
      await interaction.response.send_message(
          embed=embed_success, 
          file=discord.File(pdf_path, filename="Receipt.pdf"), 
          ephemeral=True
      )
    else:
      await interaction.response.send_message(embed=embed_success, ephemeral=True)


class ReceiptView(discord.ui.View):
  def __init__(self, bot):
    super().__init__(timeout=None)
    self.bot = bot

  @discord.ui.button(
      label="Create your receipt",
      style=discord.ButtonStyle.secondary,
      emoji="<:receipt:1542877245406978148>",
      custom_id="create_receipt_persistent_button"
  )
  async def create_receipt_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    modal = ReceiptModal()
    modal.bot_ref = self.bot
    await interaction.response.send_modal(modal)


class ReceiptCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(
      name="receipt",
      description="Send the receipt creation panel"
  )
  async def receipt(self, interaction: discord.Interaction):
    bot_avatar = self.bot.user.display_avatar.url if self.bot.user else None
    bot_name = self.bot.user.name if self.bot.user else "Bot"
    now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    footer_text = f"{bot_name} | {now_str}"

    # Vérification du rôle requis
    user_role_ids = [role.id for role in interaction.user.roles]
    if REQUIRED_ROLE_ID not in user_role_ids:
      embed_refuse = discord.Embed(
          title="<:info:1542297839026053190> Access denied Accès refusé",
          description=(
              "You do not have the required **permissions** to **use**"
              " this **command**. This **action** is **restricted** to staff members."
          ),
          color=discord.Color.from_str("#ff0000"),
      )
      if bot_avatar:
        embed_refuse.set_footer(text=footer_text, icon_url=bot_avatar)
      else:
        embed_refuse.set_footer(text=footer_text)
      await interaction.response.send_message(embed=embed_refuse, ephemeral=True)
      return

    # Envoi de la réponse éphémère de confirmation de commande exécutée ou envoi dans le salon cible
    target_channel = self.bot.get_channel(RECEIPT_CHANNEL_ID)
    
    embed_panel = discord.Embed(
        title="<:receipt:1542877245406978148> Receipt Tool",
        description=(
            "Welcome to our **server's invoicing system**! <:stars:1542297435664154695>\n\n"
            "You can **generate your receipt** using the **button below** this message. "
            "You will only need to provide a **few details** to **finalize the creation** of your receipt.\n\n"
            "<:coin:1542297155660812348> Cost to create a receipt :\n\n"
            "Generating a receipt will **deduct 1 coin** from your **personal balance**. "
            "If you **don't have any coins** in your account, you can **open a ticket** at <#1542238377837989888> to **order some**!\n\n"
            "<:info:1542297839026053190> Unfortunately, only the **French version** is currently available; "
            "our team will **soon** be making **other languages** available to you."
        ),
        color=discord.Color.from_str("#0058ff"),
    )
    if bot_avatar:
      embed_panel.set_footer(text=footer_text, icon_url=bot_avatar)
    else:
      embed_panel.set_footer(text=footer_text)

    view = ReceiptView(self.bot)

    if target_channel:
      await target_channel.send(embed=embed_panel, view=view)
      await interaction.response.send_message(
          "Le panneau de création de reçu a été envoyé avec succès dans le salon dédié !",
          ephemeral=True
      )
    else:
      await interaction.response.send_message(
          embed=embed_panel, view=view, ephemeral=True
      )


async def setup(bot):
  await bot.add_cog(ReceiptCog(bot))