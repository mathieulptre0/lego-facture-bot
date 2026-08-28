from datetime import datetime
import json
import os
import discord
from discord import app_commands, ui
from receipt import generer_ticket_pdf

# Configuration des IDs demandés
ROLE_AUTORISE_ID = 1542206470970671214
SALON_ENVOI_ID = 1542876927201644595
SALON_TICKET_SUPPORT_ID = 1542238377837989888
COINS_DB_PATH = "coins_db.json"

# Dictionnaire de traduction des mois pour la date en lettres
MOIS_FR = {
    1: "janvier",
    2: "février",
    3: "mars",
    4: "avril",
    5: "mai",
    6: "juin",
    7: "juillet",
    8: "août",
    9: "septembre",
    10: "octobre",
    11: "novembre",
    12: "décembre",
}


def charger_coins(user_id: int) -> int:
  if not os.path.exists(COINS_DB_PATH):
    return 0
  try:
    with open(COINS_DB_PATH, "r", encoding="utf-8") as f:
      data = json.load(f)
      return data.get(str(user_id), 0)
  except Exception:
    return 0


def deduire_coin(user_id: int):
  data = {}
  if os.path.exists(COINS_DB_PATH):
    try:
      with open(COINS_DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    except Exception:
      pass

  current = data.get(str(user_id), 0)
  if current > 0:
    data[str(user_id)] = current - 1

  with open(COINS_DB_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)


# --- MODAL DU FORMULAIRE ---
class ReceiptModal(ui.Modal, title="Receipt Creation"):
  item_name = ui.TextInput(
      label="Item name",
      placeholder="Nom de l'article...",
      style=discord.TextStyle.short,
      required=True,
  )
  item_price = ui.TextInput(
      label="Item price",
      placeholder="Ex: 5.99 ou 1",
      style=discord.TextStyle.short,
      required=True,
  )
  purchase_date = ui.TextInput(
      label="Date of purchase / time",
      placeholder="JJ/MM/AAAA HH:MM:SS (ex: 24/08/2026 19:35:15)",
      style=discord.TextStyle.short,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    user_id = interaction.user.id

    # 1. Vérification des coins dans coins_db.json
    coins = charger_coins(user_id)
    if coins <= 0:
      embed_err = discord.Embed(
          description=(
              "❌ You **don't have enough coins** in your account to generate a"
              " receipt. Please open a ticket to order some!"
          ),
          color=discord.Color.red(),
      )
      return await interaction.response.send_message(
          embed=embed_err, ephemeral=True
      )

    # 2. Validation et formatage du prix
    try:
      raw_price = self.item_price.value.strip().replace(",", ".")
      prix_float = float(raw_price)
      prix_str_formate = f"{prix_float:.2f} €".replace(".", ",")
    except ValueError:
      return await interaction.response.send_message(
          "❌ **Invalid price format.** Please enter a valid number (e.g.,"
          " `5.99` or `1`).",
          ephemeral=True,
      )

    # 3. Validation et parsing de la date
    date_str_brute = self.purchase_date.value.strip()
    try:
      dt_obj = datetime.strptime(date_str_brute, "%d/%m/%Y %H:%M:%S")
    except ValueError:
      return await interaction.response.send_message(
          "❌ **Invalid date format.** Please use: `JJ/MM/AAAA HH:MM:SS` (e.g.,"
          " `24/08/2026 19:35:15`).",
          ephemeral=True,
      )

    # Variables demandées pour le ticket :
    texte_date_valeur = dt_obj.strftime("%d/%m/%Y %H:%M:%S")

    jour_clean = str(dt_obj.day)
    mois_txt = MOIS_FR[dt_obj.month]
    annee_txt = dt_obj.year
    texte_date_val = f"{jour_clean} {mois_txt} {annee_txt}"

    texte_heure_val = dt_obj.strftime("%H:%M:%S")

    mm = dt_obj.strftime("%m")
    dd = dt_obj.strftime("%d")
    yyyy = dt_obj.strftime("%Y")
    texte_code_besoin = f"149-64863689-{mm}-{dd}-{yyyy} "

    # Calcul TVA (20% du prix de l'article)
    tva_float = prix_float * 0.20
    tva_str_formate = f"{tva_float:.2f} €".replace(".", ",")

    # 4. Déduction du coin
    deduire_coin(user_id)

    # 5. Appel de la fonction de génération PDF (provenant de receipt.py)
    pdf_path = generer_ticket_pdf(
        nom_article=self.item_name.value.strip(),
        prix_article_str=prix_str_formate,
        date_valeur=texte_date_valeur,
        date_lettre=texte_date_val,
        heure_valeur=texte_heure_val,
        code_avis=texte_code_besoin,
        tva_str=tva_str_formate,
    )

    if not pdf_path or not os.path.exists(pdf_path):
      return await interaction.response.send_message(
          "❌ An error occurred while generating the PDF receipt.", ephemeral=True
      )

    # 6. Embed de succès éphémère avec bouton de téléchargement
    file_to_send = discord.File(pdf_path, filename="receipt.pdf")

    embed_succes = discord.Embed(
        title="<:check:1542642100938477680> Receipt successfully created !",
        description=(
            "We have **finished creating** your invoice.\n\n"
            "<:edit:1542564664192409631> **__Updated information__:**\n\n"
            f"<:name:1542884240985948240> **Item name:**"
            f" ```{self.item_name.value.strip()}```\n"
            f"<:euro:1542884660105715842> **Item price:**"
            f" ```{prix_str_formate}```\n"
            f"<:date:1542886387358105681> **Purchase date:**"
            f" ```{texte_date_valeur}```"
        ),
        color=0x0058ff,
    )
    embed_succes.set_footer(text="Your Footer Text Here")

    class DownloadView(ui.View):

      def __init__(self, file_path):
        super().__init__(timeout=180)
        self.file_path = file_path

      @ui.button(
          label="Download the receipt",
          emoji="<:download:1542886821279563918>",
          style=discord.ButtonStyle.secondary,
      )
      async def download_btn(
          self, btn_interaction: discord.Interaction, button: ui.Button
      ):
        await btn_interaction.response.send_message(
            "📥 Here is your PDF receipt file:",
            file=discord.File(self.file_path),
            ephemeral=True,
        )

    view = DownloadView(pdf_path)
    await interaction.response.send_message(
        embed=embed_succes, view=view, file=file_to_send, ephemeral=True
    )


# --- VUE POUR LE SALON PUBLIC ---
class PersistentReceiptView(ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @ui.button(
      label="Create your receipt",
      emoji="<:receipt:1542877245406978148>",
      style=discord.ButtonStyle.secondary,
      custom_id="persistent_create_receipt_btn",
  )
  async def create_receipt_button(
      self, interaction: discord.Interaction, button: ui.Button
  ):
    await interaction.response.send_modal(ReceiptModal())


class ReceiptCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(
      name="receipt",
      description="Display the receipt creation panel in the designated channel.",
  )
  async def cmd_receipt(self, interaction: discord.Interaction):
    role = interaction.guild.get_role(ROLE_AUTORISE_ID)
    if not role or role not in interaction.user.roles:
      embed_err = discord.Embed(
          description=(
              "❌ You do not have the required permissions to execute this"
              " command."
          ),
          color=discord.Color.red(),
      )
      return await interaction.response.send_message(
          embed=embed_err, ephemeral=True
      )

    salon = self.bot.get_channel(SALON_ENVOI_ID)
    if not salon:
      return await interaction.response.send_message(
          "❌ Erreur : Le salon configuré pour l'envoi est introuvable.",
          ephemeral=True,
      )

    embed_public = discord.Embed(
        title="<:receipt:1542877245406978148> Receipt Tool",
        description=(
            "Welcome to our **server's invoicing system**!"
            " <:stars:1542297435664154695>\n\n"
            "You can **generate your receipt** using the **button below** this"
            " message. You will only need to provide a **few details** to"
            " **finalize the creation** of your receipt.\n\n"
            "<:coin:1542297155660812348> **Cost to create a receipt :**\n"
            "Generating a receipt will **deduct 1 coin** from your **personal"
            " balance**. If you **don't have any coins** in your account, you"
            f" can **open a ticket** at <#{SALON_TICKET_SUPPORT_ID}> to **order"
            " some**!\n\n"
            "<:info:1542297839026053190> Unfortunately, only the **French"
            " version** is currently available; our team will **soon** be making"
            " **other languages** available to you."
        ),
        color=0x0058ff,
    )
    embed_public.set_footer(text="Your Footer Text Here")

    await salon.send(embed=embed_public, view=PersistentReceiptView())
    await interaction.response.send_message(
        "✅ Le panneau de reçus a été envoyé avec succès dans le salon configuré"
        " !",
        ephemeral=True,
    )


async def setup(bot):
  await bot.add_cog(ReceiptCog(bot))