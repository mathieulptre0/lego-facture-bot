import asyncio
import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  # Enregistre la vue persistante pour qu'elle continue de fonctionner après un redémarrage
  from receipt_cog import ReceiptPersistentView

  bot.add_view(ReceiptPersistentView())

  print(f"Bot connecté en tant que {bot.user}")
  try:
    synced = await bot.tree.sync()
    print(f"Commandes slash synchronisées : {len(synced)} command(s)")
  except Exception as e:
    print(f"Erreur lors de la synchronisation des commandes : {e}")


async def main():
  async with bot:
    # Charge tes cogs ici (ajoute addcoin si tu l'utilises aussi sous forme de cog)
    if os.path.exists("addcoin.py"):
      try:
        await bot.load_extension("addcoin")
        print("Cog 'addcoin' chargé avec succès.")
      except Exception as e:
        print(f"Erreur chargement addcoin : {e}")

    if os.path.exists("receipt_cog.py"):
      try:
        await bot.load_extension("receipt_cog")
        print("Cog 'receipt_cog' chargé avec succès.")
      except Exception as e:
        print(f"Erreur chargement receipt_cog : {e}")

    # Remplace par ton token de bot Discord
    await bot.start("TON_TOKEN_DISCORD")


if __name__ == "__main__":
  asyncio.run(main())