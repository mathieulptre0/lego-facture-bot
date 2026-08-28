from datetime import datetime
import json
import os
import discord
from discord import app_commands
from discord.ext import commands

# Importe ta fonction de génération depuis receipt.py (renommé en receipt_generator.py par exemple)
import receipt as receipt_mod

COINS_DB_PATH = "coins_db.json"
REQUIRED_ROLE_ID = 1542206470970671214
TARGET_CHANNEL_ID = 1542876927201644595
TICKET_CHANNEL_ID = (  # Salon pour ouvrir un ticket si 0 coin
    1542238377837989888
)


def charger_coins():
  if not os.path.exists(COINS_DB_PATH):
    return {}
  with open(COINS_DB_PATH, "r", encoding="utf-8") as f:
    return json.load(f)


def sauvegarder_coins(data):
  with open(COINS_DB_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)


def formater_prix(prix_str):
  """Convertit une saisie utilisateur (ex: '1', '5.23', '1,35') en format 'X,XX €'"""
  try:
    # Remplace la virgule par un point pour le calcul float
    prix_float = float(prix_str.replace(",", "."))
    return f"{prix_float:.2f}".replace(".", ",") + " €", prix_float
  except ValueError:
    return "0,00 €", 0.0


def convertir_date_en_lettres(date_str):
  """Convertit '27/09/2018' en '27 septembre 2018'"""
  mois = {
      "01": "janvier",
      "02": "février",
      "03": "mars",
      "04": "avril",
      "05": "mai",
      "06": "juin",
      "07": "juillet",
      "08": "août",
      "09": "septembre",
      "10": "octobre",
      "11": "novembre",
      "12": "décembre",
  }
  try:
    parts = date_str.split("/")
    jour = str(int(parts[0]))  # Enlève le zéro initial si besoin
    nom_mois = mois.get(parts[1], "")
    annee = parts[2]
    return f"{jour} {nom_mois} {annee}"
  except Exception:
    return date_str


# Formulaire Discord (Modal)
class ReceiptModal(discord.ui.Modal, title="Receipt Creation"):
  item_name = discord.ui.TextInput(
      label="Item name",
      placeholder="Ex: Porte-clés Miles Morales",
      required=True,
      max_length=100,
  )
  item_price = discord.ui.TextInput(
      label="Item price", placeholder="Ex: 5.99 ou 1", required=True, max_length=10
  )
  purchase_date = discord.ui.TextInput(
      label="Date of purchase / time",
      placeholder="Ex: 24/08/2026 19:35:15",
      required=True,
      max_length=25,
  )

  async def on_submit(self, interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    coins_data = charger_coins()
    solde = coins_data.get(user_id, 0)

    # Vérification des coins
    if solde < 1:
      embed_err = discord.Embed(
          description=(
              "❌ **You do not have enough coins** in your personal balance to"
              " generate a receipt. Please **open a ticket** at"
              f" <#{TICKET_CHANNEL_ID}> to **order some**!"
          ),
          color=discord.Color.red(),
      )
      return await interaction.response.send_message(
          embed=embed_err, ephemeral=True
      )

    # Déduction d'un coin
    coins_data[user_id] = solde - 1
    sauvegarder_coins(coins_data)

    # Récupération des valeurs du formulaire
    nom_art = self.item_name.value
    prix_brut = self.item_price.value
    date_heure_brute = self.purchase_date.value  # Format "24/08/2026 19:35:15"

    prix_formate, prix_float = formater_prix(prix_brut)

    # Calcul TVA (20%)
    tva_float = prix_float * 0.20
    tva_formatee = f"{tva_float:.2f}".replace(".", ",") + " €"

    # Séparation date et heure
    try:
      date_part, heure_part = date_heure_brute.split(" ")
    except ValueError:
      date_part = "24/08/2026"
      heure_part = "19:35:15"

    date_en_lettres = convertir_date_en_lettres(date_part)

    # Génération du code d'avis dynamique (ex: 149-64863689-01-25-2017)
    try:
      d_parts = date_part.split("/")
      code_date_fmt = f"{d_parts[1]}-{d_parts[0]}-{d_parts[2]}"
    except Exception:
      code_date_fmt = "08-24-2026"
    code_avis = f"149-64863689-{code_date_fmt} "

    # Injection dynamique dans receipt.py (en modifiant les variables globales de receipt_mod si configuré,
    # ou en passant les variables directement à ta fonction de génération modifiée)
    # Note : Assure-toi d'adapter ta fonction `executer_generation_complete` dans receipt.py pour accepter ces paramètres.
    receipt_mod.executer_generation_complete(
        article=nom_art,
        prix=prix_formate,
        tva=tva_formatee,
        date_heure=date_heure_brute,
        date_lettres=date_en_lettres,
        heure=heure_part,
        code_besoin=code_avis,
    )

    pdf_path = r"C:\Users\leazy\Desktop\lego facture bot\Receipt.pdf"
    file = discord.File(pdf_path, filename="Receipt.pdf")

    # Embed de succès éphémère
    embed_succes = discord.Embed(
        title="<:check:1542642100938477680> Receipt successfully created !",
        description=(
            "We have **finished creating** your invoice.\n\n<:edit:1542564664192409631>"
            " **__Updated information__:**\n\n<:name:1542884240985948240>"
            f" **Item name:** ```{nom_art}```\n<:euro:1542884660105715842>"
            f" **Item price:** ```{prix_formate}```\n<:date:1542886387358105681>"
            f" **Purchase date:** ```{date_heure_brute}```"
        ),
        color=int("0058ff", 16),
    )
    # Ajouter le footer personnalisé de ton serveur ici si besoin
    # embed_succes.set_footer(text="Ton Footer")

    view_dl = discord.ui.View()
    # Bouton de téléchargement pointant vers le fichier généré (via l'attachement)
    btn_download = discord.ui.Button(
        label="Download the receipt",
        style=discord.ButtonStyle.secondary,
        emoji="<:download:1542886821279563918>",
    )

    # Callback pour le bouton de téléchargement ou simple envoi du fichier avec l'embed
    async def download_callback(interaction: discord.Interaction):
      await interaction.response.send_message(
          file=discord.File(pdf_path), ephemeral=True
      )

    btn_download.callback = download_callback
    view_dl.add_item(btn_download)

    await interaction.response.send_message(
        embed=embed_succes, file=file, view=view_dl, ephemeral=True
    )


# Vue contenant le bouton "Create your receipt"
class ReceiptView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="Create your receipt",
      style=discord.ButtonStyle.secondary,
      emoji="<:receipt:1542877245406978148>",
      custom_id="create_receipt_persistent_button",
  )
  async def create_receipt_button(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(ReceiptModal())


# Commande slash /receipt
@app_commands.command(
    name="receipt", description="Affiche le panneau de génération de facture"
)
async def receipt_command(interaction: discord.Interaction):
  # Vérification du rôle requis
  role = interaction.guild.get_role(REQUIRED_ROLE_ID)
  if not role or role not in interaction.user.roles:
    embed_error = discord.Embed(
        description="❌ Vous n'avez pas la permission d'exécuter cette commande.",
        color=discord.Color.red(),
    )
    return await interaction.response.send_message(
        embed=embed_error, ephemeral=True
    )

  # Envoi du message dans le salon cible (1542876927201644595)
  salon = interaction.client.get_channel(TARGET_CHANNEL_ID)
  if not salon:
    return await interaction.response.send_message(
        "❌ Salon cible introuvable.", ephemeral=True
    )

  embed_panel = discord.Embed(
      title="<:receipt:1542877245406978148> Receipt Tool",
      description=(
          "Welcome to our **server's invoicing system**!"
          " <:stars:1542297435664154695>\n\nYou can **generate your receipt** using"
          " the **button below** this message. You will only need to provide a"
          " **few details** to **finalize the creation** of your"
          " receipt.\n\n<:coin:1542297155660812348> Cost to create a"
          " receipt :\n\nGenerating a receipt will **deduct 1 coin** from your"
          " **personal balance**. If you **don't have any coins** in your"
          " account, you can **open a ticket** at <#"
          f"{TICKET_CHANNEL_ID}> to **order some**!\n\n<:info:1542297839026053190>"
          " Unfortunately, only the **French version** is currently available;"
          " our team will **soon** be making **other languages** available to"
          " you."
      ),
      color=int("0058ff", 16),
  )
  # embed_panel.set_footer(text="Ton Footer")

  view = ReceiptView()
  await salon.send(embed=embed_panel, view=view)
  await interaction.response.send_message(
      "✅ Le panneau de facture a été envoyé avec succès dans le salon dédié !",
      ephemeral=True,
  )