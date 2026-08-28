import asyncio
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

INTENTS = discord.Intents.default()
INTENTS.guilds = True
INTENTS.members = True

client = commands.Bot(command_prefix="!", intents=INTENTS)


@client.event
async def on_ready():
  print(f"Connecté en tant que {client.user}")
  # Chargement des extensions (cogs)
  try:
    await client.load_extension("addcoin")
    await client.load_extension("removecoin")
    await client.load_extension("discount")
    await client.load_extension("removediscount")
    await client.load_extension("discountlist")
    await client.load_extension("ticket")
    await client.load_extension("invoice")
    await client.load_extension("receipt_cog")
    print("Commandes chargées avec succès !")
  except Exception as e:
    print(f"Erreur lors du chargement des extensions : {e}")

  # Synchronisation des commandes slash avec Discord
  try:
    synced = await client.tree.sync()
    print(f"Arbre slash sync : {len(synced)} commandes synchronisées.")
  except Exception as e:
    print(e)


client.run(TOKEN)