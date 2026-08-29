from datetime import datetime
import os
subprocess = __import__("subprocess")
import discord
from discord import app_commands, ui
from discord.ext import commands
from receipt import generer_ticket_pdf
# Import des fonctions de ta base de données MongoDB
from database import get_user_coins, update_user_coins

ROLE_AUTORISE_ID = 1542206470970671214
SALON_ENVOI_ID = 1542876927201644595
SALON_TICKET_SUPPORT_ID = 1542238377837989888
SALON_ARCHIVE_TICKETS_ID = 1542954377718009886

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


class ReceiptModal(ui.Modal, title="Receipt Creation"):
  item_name = ui.TextInput(
      label="Item name",
      placeholder="ex: Lamborghini Sián FKP 37",
      style=discord.TextStyle.short,
      required=True,
  )
  item_price = ui.TextInput(
      label="Item price",
      placeholder="Ex: 5.99 or 1",
      style=discord.TextStyle.short,
      required=True,
  )
  purchase_date = ui.TextInput(
      label="Date of purchase / time",
      placeholder="DD/MM/YYYY HH:MM:SS (ex: 24/08/2026 19:35:15)",
      style=discord.TextStyle.short,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    bot_user = interaction.client.user
    bot_name = bot_user.name if bot_user else "Receipt Tool"
    bot_avatar = bot_user.display_avatar.url if bot_user else None
    now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    footer_text = f"{bot_name} | {now_str}"

    try:
      user_id = interaction.user.id
      # Utilisation directe de MongoDB pour récupérer les coins
      coins = get_user_coins(user_id)
      if coins <= 0:
        embed_err = discord.Embed(
            description=(
                "❌ You **don't have enough coins** in your account to generate a"
                " receipt. Please open a ticket to order some!"
            ),
            color=discord.Color.red(),
        )
        return await interaction.followup.send(embed=embed_err, ephemeral=True)

      embed_loading = discord.Embed(
          title="<:hourglass:1542971361306222682> **Generating receipt...**",
          description=(
              "Please **wait a moment** while we **process your request** and"
              " **generate** your PDF receipt."
          ),
          color=0x0058ff,
      )
      if bot_avatar:
        embed_loading.set_footer(text=footer_text, icon_url=bot_avatar)
      else:
        embed_loading.set_footer(text=footer_text)

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
        return await loading_message.edit(embed=embed_bad_price)

      date_str_brute = self.purchase_date.value.strip()
      try:
        dt_obj = datetime.strptime(date_str_brute, "%d/%m/%Y %H:%M:%S")
      except ValueError:
        embed_bad_date = discord.Embed(
            description=(
                "❌ **Invalid date format.** Please use: `DD/MM/YYYY HH:MM:SS`"
                " (e.g., `24/08/2026 19:35:15`)."
            ),
            color=discord.Color.red(),
        )
        return await loading_message.edit(embed=embed_bad_date)

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

      # Déduit 1 coin via MongoDB (-1)
      update_user_coins(user_id, -1)

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
        return await loading_message.edit(embed=embed_gen_err)

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
      if bot_avatar:
        embed_succes.set_footer(text=footer_text, icon_url=bot_avatar)
      else:
        embed_succes.set_footer(text=footer_text)

      salon_archives = interaction.client.get_channel(SALON_ARCHIVE_TICKETS_ID)
      attachment_url = None
      if salon_archives:
        file_archive = discord.File(pdf_path, filename="receipt.pdf")
        archive_msg = await salon_archives.send(
            content=(
                f"📄 Ticket généré par {interaction.user.mention}"
                f" (`{interaction.user.id}`)"
            ),
            file=file_archive,
            embed=embed_succes,
        )
        if archive_msg.attachments:
          attachment_url = archive_msg.attachments[0].url

      if attachment_url:

        class DownloadLinkView(ui.View):

          def __init__(self, url: str):
            super().__init__(timeout=180)
            self.add_item(
                ui.Button(
                    label="Download the receipt",
                    emoji="<:download:1542886821279563918>",
                    style=discord.ButtonStyle.link,
                    url=url,
                )
            )

        await loading_message.edit(
            embed=embed_succes, view=DownloadLinkView(attachment_url)
        )
      else:
        await loading_message.edit(embed=embed_succes, view=None)

    except Exception as e:
      print(f"Erreur dans le modal : {e}")


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

    bot_user = self.bot.user or interaction.client.user
    bot_name = bot_user.name if bot_user else "Receipt Tool"
    bot_avatar = bot_user.display_avatar.url if bot_user else None
    now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    footer_text = f"{bot_name} | {now_str}"

    embed_public = discord.Embed(
        title="<:receipt:1542877245406978148> Receipt Tool",
        description=(
            "Welcome to our **server's invoicing system**!"
            " <:stars:1542297435664154695>\n\n"
            "You can **generate your receipt** using the **button below** this"
            " message. You will only need to provide a **few details** to"
            " **finalize the creation** of your receipt.\n\n"
            "<:coin:1542297155660812348> **__Cost to create a receipt__ :**\n"
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
    if bot_avatar:
      embed_public.set_footer(text=footer_text, icon_url=bot_avatar)
    else:
      embed_public.set_footer(text=footer_text)

    await salon.send(embed=embed_public, view=PersistentReceiptView())
    await interaction.response.send_message(
        "✅ Le panneau de reçus a été envoyé avec succès dans le salon configuré"
        " !",
        ephemeral=True,
    )


async def setup(bot):
  await bot.add_cog(ReceiptCog(bot))