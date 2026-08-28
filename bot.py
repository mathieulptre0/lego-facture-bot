import datetime
import json
import os
import discord
from discord import app_commands
from discord.ext import commands
from receipt import executer_generation_complete

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

COINS_DB_PATH = "coins_db.json"
REQUIRED_ROLE_ID = 1542206470970671214
CONFIG_CHANNEL_ID = 1542876927201644595
TICKET_CHANNEL_ID = 1542238377837989888

# Remplace par l'ID réel de ton serveur Discord pour forcer l'affichage immédiat de /receipt
GUILD_ID = discord.Object(id=154220000000000000)


def charger_coins():
  if not os.path.exists(COINS_DB_PATH):
    return {}
  with open(COINS_DB_PATH, "r", encoding="utf-8") as f:
    try:
      return json.load(f)
    except json.JSONDecodeError:
      return {}


def sauvegarder_coins(data):
  with open(COINS_DB_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)


class ReceiptModal(discord.ui.Modal, title="Create your receipt"):
  item_name = discord.ui.TextInput(
      label="Item name",
      placeholder="Ex: Porte-clés Miles Morales",
      required=True,
      max_length=100,
  )
  item_price = discord.ui.TextInput(
      label="Item price", placeholder="Ex: 5.99 ou 1", required=True, max_length=20
  )
  purchase_date = discord.ui.TextInput(
      label="Date of purchase / time",
      placeholder="DD/MM/YYYY HH:MM:SS (ex: 24/08/2026 19:35:15)",
      required=True,
      max_length=30,
  )

  async def on_submit(self, interaction: discord.Interaction):
    user_id_str = str(interaction.user.id)
    coins_data = charger_coins()
    user_coins = coins_data.get(user_id_str, 0)

    if user_coins < 1:
      error_embed = discord.Embed(
          title="Error",
          description=(
              "You **don't have enough coins** in your account to generate a"
              f" receipt. Please order some at <#{TICKET_CHANNEL_ID}>!"
          ),
          color=discord.Color.red(),
      )
      await interaction.response.send_message(embed=error_embed, ephemeral=True)
      return

    coins_data[user_id_str] = user_coins - 1
    sauvegarder_coins(coins_data)

    raw_price = self.item_price.value.strip().replace(",", ".")
    try:
      price_float = float(raw_price)
    except ValueError:
      coins_data[user_id_str] = user_coins
      sauvegarder_coins(coins_data)
      await interaction.response.send_message(
          embed=discord.Embed(
              title="Error",
              description=(
                  "Invalid **item price format**. Please use numbers (e.g.,"
                  " 5.99)."
              ),
              color=discord.Color.red(),
          ),
          ephemeral=True,
      )
      return

    formatted_price = f"{price_float:.2f}".replace(".", ",") + " €"
    tva_float = price_float * 0.20
    formatted_tva = f"{tva_float:.2f}".replace(".", ",") + " €"

    name = self.item_name.value.strip()
    date_time_str = self.purchase_date.value.strip()

    try:
      dt = datetime.datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S")
    except ValueError:
      try:
        dt = datetime.datetime.strptime(date_time_str, "%d/%m/%Y")
        date_time_str += " 00:00:00"
      except ValueError:
        coins_data[user_id_str] = user_coins
        sauvegarder_coins(coins_data)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Error",
                description=(
                    "Invalid **date/time format**. Please use `DD/MM/YYYY"
                    " HH:MM:SS`."
                ),
                color=discord.Color.red(),
            ),
            ephemeral=True,
        )
        return

    mois_fr = {
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
    date_long_fr = f"{dt.day} {mois_fr[dt.month]} {dt.year}"
    heure_str = dt.strftime("%H:%M:%S")
    code_avis = f"149-64863689-{dt.month:02d}-{dt.day:02d}-{dt.year} "

    executer_generation_complete(
        item_name=name,
        item_price=formatted_price,
        tva_price=formatted_tva,
        date_time=date_time_str,
        date_long=date_long_fr,
        heure=heure_str,
        code_besoin=code_avis,
    )

    pdf_path = os.path.join(
        r"C:\Users\leazy\Desktop\lego facture bot", "Receipt.pdf"
    )

    success_embed = discord.Embed(
        title=(
            "<:check:1542642100938477680> Receipt successfully created !"
        ),
        description=(
            "We have **finished creating** your invoice.\n\n"
            "<:edit:1542564664192409631> **__Updated information__:**\n\n"
            f"<:name:1542884240985948240> **Item name:** ```{name}```\n"
            f"<:euro:1542884660105715842> **Item price:** ```{formatted_price}```\n"
            f"<:date:1542886387358105681> **Purchase date:** ```{date_time_str}```"
        ),
        color=0x0058FF,
    )
    success_embed.set_footer(text="Système de facturation sécurisé")

    class DownloadView(discord.ui.View):

      def __init__(self):
        super().__init__(timeout=180)
        self.add_item(
            discord.ui.Button(
                label="Download the receipt",
                emoji="<:download:1542886821279563918>",
                style=discord.ButtonStyle.grey,
                url="attachment://Receipt.pdf",
            )
        )

    file = discord.File(pdf_path, filename="Receipt.pdf")
    await interaction.response.send_message(
        embed=success_embed, file=file, view=DownloadView(), ephemeral=True
    )


class ReceiptPersistentView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="Create your receipt",
      emoji="<:receipt:1542877245406978148>",
      style=discord.ButtonStyle.grey,
      custom_id="persistent_create_receipt_btn",
  )
  async def create_receipt_button(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(ReceiptModal())


@bot.event
async def on_ready():
  bot.add_view(ReceiptPersistentView())
  try:
    synced = await bot.tree.sync(guild=GUILD_ID)
    print(
        f"Commande /receipt synchronisée avec succès sur le serveur :"
        f" {len(synced)} command(s)"
    )
  except Exception as e:
    print(f"Erreur de synchronisation : {e}")
  print(f"Bot connecté en tant que {bot.user}")


@bot.tree.command(
    name="receipt",
    description="Envoyer le panneau de génération de reçus",
    guild=GUILD_ID,
)
async def receipt_command(interaction: discord.Interaction):
  role = interaction.guild.get_role(REQUIRED_ROLE_ID)
  if not role or role not in interaction.user.roles:
    error_embed = discord.Embed(
        title="Error",
        description="You do not have permission to execute this command.",
        color=discord.Color.red(),
    )
    await interaction.response.send_message(embed=error_embed, ephemeral=True)
    return

  channel = bot.get_channel(CONFIG_CHANNEL_ID)
  if not channel:
    await interaction.response.send_message(
        "Salon de configuration introuvable.", ephemeral=True
    )
    return

  embed = discord.Embed(
      title=(
          "<:receipt:1542877245406978148> Welcome to our server's invoicing"
          " system! <:stars:1542297435664154695>"
      ),
      description=(
          "You can **generate your receipt** using the **button below** this"
          " message. You will only need to provide a **few details** to"
          " **finalize the creation** of your receipt.\n\n"
          "<:coin:1542297155660812348> **Cost to create a receipt** :\n\n"
          "Generating a receipt will **deduct 1 coin** from your **personal"
          " balance**. If you **don't have any coins** in your account, you can"
          f" **open a ticket** at <#{TICKET_CHANNEL_ID}> to **order some**!\n\n"
          "<:info:1542297839026053190> Unfortunately, only the **French version**"
          " is currently available; our team will **soon** be making **other"
          " languages** available to you."
      ),
      color=0x0058FF,
  )
  embed.set_footer(text="Système de facturation sécurisé")

  await channel.send(embed=embed, view=ReceiptPersistentView())
  await interaction.response.send_message(
      "Le panneau de reçus a été envoyé avec succès dans le salon dédié !",
      ephemeral=True,
  )


# Remplace par ton token de bot Discord
# bot.run("TON_TOKEN_DISCORD")