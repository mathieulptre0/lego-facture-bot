from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands

ROLE_AUTORISE_ID = 1542206470970671214
SALON_ENVOI_TOS_ID = 1543038431838478396


class TosCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(
      name="tos",
      description="Display the Terms of Services in the designated channel.",
  )
  async def cmd_tos(self, interaction: discord.Interaction):
    # Vérification du rôle autorisé
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

    # Récupération du salon d'envoi
    salon = self.bot.get_channel(SALON_ENVOI_TOS_ID)
    if not salon:
      return await interaction.response.send_message(
          "❌ Erreur : Le salon configuré pour les TOS est introuvable.",
          ephemeral=True,
      )

    # Configuration du footer (identique aux autres cogs)
    bot_user = self.bot.user or interaction.client.user
    bot_name = bot_user.name if bot_user else "Receipt Tool"
    bot_avatar = bot_user.display_avatar.url if bot_user else None
    now_str = datetime.now().strftime("%d/%m/%Y at %H:%M")
    footer_text = f"{bot_name} | {now_str}"

    # Construction de l'embed TOS avec une ligne vide sous chaque titre
    embed_tos = discord.Embed(
        title="<:tos:1542297487346376834> Terms Of Services",
        description=(
            "By **accessing or using** the Discord server, you **acknowledge** that"
            " you have **read this agreement** and agree to be **bound by its"
            " provisions**, as well as by all **applicable laws and regulations**."
            " If you **do not agree** to any of the provisions set forth herein,"
            " you must **immediately cease** all use of the **Discord server**.\n\n"
            "<:number1:1543052524724953108> **__Payment and Pricing__ :**\n\n"
            "> Any **purchase** made on our **store** is subject to the"
            " **prices in effect** at the time of the order. You agree to"
            " **provide accurate, complete, and up-to-date** payment information"
            " and to **complete the transaction** within the **allotted"
            " time**.\n\n"
            "<:number2:1543052500071092416> **__Refunds__ :**\n\n"
            "> Unless **otherwise stated** or subject to **specific"
            " conditions** specified at the time of purchase, **refunds are"
            " generally not granted**."
            "It is your **responsibility** to carefully **review the service"
            " description** as well as the applicable **refund policy** prior"
            " to placing any order.\n\n"
            "<:number3:1543052592018362388> **__Chargebacks__ :**\n\n"
            "> In the event of a **payment dispute**, chargeback, or any claim"
            " related to a transaction initiated by you, we **reserve the"
            " right** to immediately **suspend or terminate** your access to"
            " the **services** provided via our store, without prejudice to any"
            " other available remedy.\n\n"
            "<:number4:1543052682082652161> **__Access Termination__ :**\n\n"
            "> We **reserve the right** to **terminate your purchases** and your"
            " access to the **store and associated services** in the event"
            " of a **violation of this agreement** or **unauthorized use**"
            " of our services.\n\n"
            "<:number5:1543052758234439772> **__Modifications__ :**\n\n"
            "> We **reserve the right** to **modify or update** this Agreement"
            " at any time and **without prior notice**. Continued use of our"
            " **Discord** after the **publication of any modifications**"
            " constitutes **acceptance of the revised terms**.\n\n\n"
            "By **accepting these modifications**, you **acknowledge and"
            " agree** to the **risks and responsibilities** associated with the"
            " **continued use** of the services."
        ),
        color=0x0058ff,
    )

    if bot_avatar:
      embed_tos.set_footer(text=footer_text, icon_url=bot_avatar)
    else:
      embed_tos.set_footer(text=footer_text)

    # Envoi public dans le salon TOS
    await salon.send(embed=embed_tos)

    # Réponse de confirmation cachée (éphémère) pour l'admin qui a tapé la commande
    await interaction.response.send_message(
        "✅ Le message des Terms Of Services a été envoyé avec succès dans le"
        " salon configuré !",
        ephemeral=True,
    )


async def setup(bot):
  await bot.add_cog(TosCog(bot))