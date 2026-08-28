import json
import os
import discord
from discord.ext import commands
import receipt  # Importe ton fichier receipt.py fourni

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="/", intents=intents)

# IDs spécifiés
ROLE_ID = 1542206470970671214
CHANNEL_PANEL_ID = 1542876927201644595
TICKET_CHANNEL_ID = 1542238377837989888
DB_PATH = "coins_db.json"


def charger_coins(user_id: int) -> int:
  """Charge le nombre de coins d'un utilisateur depuis coins_db.json[cite: 5]."""
  if not os.path.exists(DB_PATH):
    return 0
  try:
    with open(DB_PATH, "r", encoding="utf-8") as f:
      data = json.load(f)
      return data.get(str(user_id), 0)
  except Exception:
    return 0


def retirer_coin(user_id: int):
  """Retire 1 coin à l'utilisateur dans coins_db.json[cite: 5]."""
  data = {}
  if os.path.exists(DB_PATH):
    try:
      with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    except Exception:
      pass

  user_key = str(user_id)
  if user_key in data and data[user_key] > 0:
    data[user_key] -= 1

  with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)


class ReceiptModal(discord.ui.Modal, title="Receipt Creation"):
  item_name = discord.ui.TextInput(
      label="Item name",
      placeholder="Ex: Porte-clés Miles Morales",
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
      placeholder="Ex: 24/08/2026 19:35:15",
      required=True,
      max_length=30,
  )

  async def on_submit(self, interaction: discord.Interaction):
    user_id = interaction.user.id

    # 1. Vérification des coins dans coins_db.json[cite: 5]
    coins = charger_coins(user_id)
    if coins <= 0:
      embed_err = discord.Embed(
          title="Error",
          description=(
              f"You **do not have enough coins** in your account to create a"
              f" receipt. Please **open a ticket** at"
              f" <#{TICKET_CHANNEL_ID}> to **order some**!"
          ),
          color=discord.Color.red(),
      )
      await interaction.response.send_message(embed=embed_err, ephemeral=True)
      return

    # 2. Retirer 1 coin[cite: 5]
    retirer_coin(user_id)

    # Récupération et formatage des données du formulaire[cite: 5]
    nom_article = self.item_name.value.strip()
    raw_price = self.item_price.value.strip().replace(",", ".")

    try:
      prix_float = float(raw_price)
    except ValueError:
      prix_float = 0.0

    prix_formate = f"{prix_float:.2f}".replace(".", ",") + " €"
    tva_float = prix_float * 0.20
    tva_formatee = f"{tva_float:.2f}".replace(".", ",") + " €"

    date_str = self.purchase_date.value.strip()

    try:
      part_date, part_heure = date_str.split(" ")
      jour, mois, annee = part_date.split("/")

      mois_dict = {
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
      nom_mois = mois_dict.get(mois, "août")
      date_lettres = f"{int(jour)} {nom_mois} {annee}"
    except Exception:
      date_lettres = "24 août 2026"
      part_heure = "19:35:15"
      mois, jour, annee = "08", "24", "2026"

    code_avis = f"149-64863689-{mois}-{jour}-{annee} "

    # 3. Injection des variables modifiées dans receipt.py[cite: 5]
    receipt.texte_article = nom_article
    receipt.texte_p1 = prix_formate
    receipt.texte_tot_payer = prix_formate
    receipt.texte_599e = prix_formate
    receipt.texte_1e_nouveau = tva_formatee
    receipt.texte_1e = tva_formatee
    receipt.texte_code_besoin = code_avis
    receipt.texte_date_valeur = date_str
    receipt.texte_date_val = date_lettres
    receipt.texte_heure_val = part_heure

    # 4. Exécution de la génération du PDF[cite: 5]
    try:
      receipt.executer_generation_complete()
    except Exception as e:
      embed_err = discord.Embed(
          title="Error",
          description=(
              f"An error occurred while generating the PDF: **{str(e)}**"
          ),
          color=discord.Color.red(),
      )
      await interaction.response.send_message(embed=embed_err, ephemeral=True)
      return

    # 5. Envoi du fichier PDF généré[cite: 5]
    pdf_path = os.path.join(
        r"C:\Users\leazy\Desktop\lego facture bot", "Receipt.pdf"
    )

    embed_success = discord.Embed(
        title="<:check:1542642100938477680> Receipt successfully created !",
        description=(
            "We have **finished creating** your invoice.\n\n"
            "<:edit:1542564664192409631> **__Updated information__:**\n\n"
            f"<:name:1542884240985948240> **Item name:** ```{nom_article}```\n\n"
            f"<:euro:1542884660105715842> **Item price:**"
            f" ```{prix_formate}```\n\n"
            f"<:date:1542886387358105681> **Purchase date:** ```{date_str}```"
        ),
        color=0x0058FF,
    )
    embed_success.set_footer(text="LEGO® Invoicing System")

    file = discord.File(pdf_path, filename="Receipt.pdf")
    await interaction.response.send_message(
        embed=embed_success, file=file, ephemeral=True
    )


class ReceiptView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="Create your receipt",
      style=discord.ButtonStyle.secondary,
      emoji="<:receipt:1542877245406978148>",
      custom_id="create_receipt_button",
  )
  async def create_receipt(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(ReceiptModal())


@bot.command(name="receipt")
async def receipt_cmd(ctx):
  # Vérification du rôle requis[cite: 5]
  role = ctx.guild.get_role(ROLE_ID)
  if not role or role not in ctx.author.roles:
    embed_error = discord.Embed(
        title="Error",
        description="You do not have permission to execute this command.",
        color=discord.Color.red(),
    )
    await ctx.send(embed=embed_error, delete_after=10)
    return

  # Envoi de l'embed principal dans le salon configuré[cite: 5]
  channel = bot.get_channel(CHANNEL_PANEL_ID)
  if not channel:
    await ctx.send("Salon introuvable.", ephemeral=True)
    return

  embed = discord.Embed(
      title=(
          "<:receipt:1542877245406978148> Welcome to our **server's invoicing"
          " system**! :stars: 1542297435664154695"
      ),
      description=(
          "You can **generate your receipt** using the **button below** this"
          " message. You will only need to provide a **few details** to"
          " **finalize the creation** of your receipt.\n\n"
          ":coin: 1542297155660812348 Cost to create a receipt :\n\n"
          "Generating a receipt will **deduct 1 coin** from your **personal"
          " balance**. If you **don't have any coins** in your account, you can"
          f" **open a ticket** at <#{TICKET_CHANNEL_ID}> to **order some**!\n\n"
          ":info: 1542297839026053190 Unfortunately, only the **French version**"
          " is currently available; our team will **soon** be making **other"
          " languages** available to you."
      ),
      color=0x0058FF,
  )
  embed.set_footer(text="LEGO® Invoicing System")

  view = ReceiptView()
  await channel.send(embed=embed, view=view)
  await ctx.message.delete()


@bot.event
async def on_ready():
  print(f"Bot connecté en tant que {bot.user}")


bot.run("TON_TOKEN_DISCORD")