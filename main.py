import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from receipt_cog import PersistentReceiptView

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

INTENTS = discord.Intents.default()
INTENTS.guilds = True
INTENTS.members = True

client = commands.Bot(command_prefix="!", intents=INTENTS)


@client.event
async def on_ready():
  # Enregistrement de la vue persistante pour les boutons globaux
  client.add_view(PersistentReceiptView())
  print(f"Bot connecté en tant que {client.user} (ID: {client.user.id})")
  print("Prêt à générer des reçus.")

  # Synchronisation des commandes slash avec Discord
  try:
    synced = await client.tree.sync()
    print(f"Commandes slash synchronisées : {len(synced)}")
  except Exception as e:
    print(f"Erreur lors de la synchronisation des commandes : {e}")


async def main():
  async with client:
    # Chargement du cog des reçus
    await client.load_extension("receipt_cog")
    await client.start(TOKEN)


if __name__ == "__main__":
  import asyncio

  asyncio.run(main())