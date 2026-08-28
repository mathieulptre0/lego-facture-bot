from datetime import datetime
import json
import os
from dotenv import load_dotenv
import discord
from discord import app_commands, ui
from discord.ext import commands
from receipt import generer_ticket_pdf

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

INTENTS = discord.Intents.default()
INTENTS.guilds = True
INTENTS.members = True

client = commands.Bot(command_prefix="!", intents=INTENTS)

ROLE_AUTORISE_ID = 1542206470970671214
SALON_ENVOI_ID = 1542876927201644595
SALON_TICKET_SUPPORT_ID = 1542238377837989888
COINS_DB_PATH = "coins_db.json"

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
    # On commence par différer pour prendre le temps de tout traiter
    await interaction.response.defer(ephemeral=True)

    try:
      user_id = interaction.user.id
      coins = charger_coins(user_id)
      if coins <= 0:
        embed_err = discord.Embed(
            description=(
                "❌ You **don't have enough coins** in your account to generate a"
                " receipt. Please open a ticket to order some!"
            ),
            color=discord.Color.red(),
        )
        await interaction.followup.send(embed=embed_err, ephemeral=True)
        return

      # Envoi de l'embed d'attente
      embed_loading = discord.Embed(
          title="⌛ **Generating receipt...**",
          description=(
              "Please **wait a moment** while we **process your request** and"
              " **generate** your PDF receipt."
          ),
          color=0x0058ff,
      )
      embed_loading.set_footer(text="Your Footer Text Here")
      
      loading_message = await interaction.followup.send(
          embed=embed_loading, ephemeral=True
      )

      try:
        raw_price = self.item_price.value.strip().replace(",", ".")
        prix_float = float(raw_price)
        prix_str_formate = f"{prix_float:.2f} €".replace(".", ",")
      except ValueError:
        embed_bad_price = discord.Embed(
            description=(
                "❌ **Invalid price format.** Please enter a valid number (e.g.,"
                " `5.99` or `1`)."
            ),
            color=discord.Color.red(),
        )
        await loading_message.edit(embed=embed_bad_price)
        return

      date_str_brute = self.purchase_date.value.strip()
      try:
        dt_obj = datetime.strptime(date_str_brute, "%d/%m/%Y %H:%M:%S")
      except ValueError:
        embed_bad_date = discord.Embed(
            description=(
                "❌ **Invalid date format.** Please use: `JJ/MM/AAAA HH:MM:SS`"
                " (e.g., `24/08/2026 19:35:15`)."
            ),
            color=discord.Color.red(),
        )
        await loading_message.edit(embed=embed_bad_date)
        return

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
      tva_float = prix_float * 0.20
      tva_str_formate = f"{tva_float:.2f} €".replace(".", ",")

      deduire_coin(user_id)

      # Génération du PDF
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
        embed_gen_err = discord.Embed(
            description="❌ An error occurred while generating the PDF receipt.",
            color=discord.Color.red(),
        )
        await loading_message.edit(embed=embed_gen_err)
        return

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
      await loading_message.edit(
          embed=embed_succes, view=view, attachments=[file_to_send]
      )

    except Exception as e:
      print(f"Erreur critique dans le modal ReceiptModal : {e}")
      try:
        await interaction.followup.send(
            f"❌ Une erreur interne est survenue : `{e}`", ephemeral=True
        )
      except Exception:
        pass


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


@client.tree.command(
    name="receipt",
    description="Display the receipt creation panel in the designated channel.",
)
async def cmd_receipt(interaction: discord.Interaction):
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

  salon = client.get_channel(SALON_ENVOI_ID)
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


@client.event
async def on_ready():
  print(f"Connecté en tant que {client.user}")
  try:
    await client.load_extension("addcoin")
    await client.load_extension("removecoin")
    await client.load_extension("discount")
    await client.load_extension("removediscount")
    await client.load_extension("discountlist")
    await client.load_extension("ticket")
    await client.load_extension("invoice")
    print("Extensions chargées avec succès !")
  except Exception as e:
    print(f"Erreur lors du chargement des extensions : {e}")

  try:
    synced = await client.tree.sync()
    print(f"Arbre slash sync : {len(synced)} commandes synchronisées.")
  except Exception as e:
    print(e)


client.run(TOKEN)