import discord
from discord.ext import commands
# Assure-toi que tu as une collection ou une fonction MongoDB pour gérer ça, 
# ou on peut utiliser une structure simple connectée à ta base de données.
from database import get_db

ROLE_ARRIVEE_ID = 1542206549974585374

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = get_db()
        self.left_roles_collection = self.db["left_member_roles"] if self.db is not None else None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # 1. Ajouter le rôle par défaut pour les nouveaux/revenants
        role_arrivee = member.guild.get_role(ROLE_ARRIVEE_ID)
        if role_arrivee:
            try:
                await member.add_roles(role_arrivee, reason="Rôle automatique à l'arrivée")
            except Exception as e:
                print(f"Erreur lors de l'attribution du rôle d'arrivée : {e}")

        # 2. Restaurer les anciens rôles si le membre était déjà venu
        if self.left_roles_collection is not None:
            data = self.left_roles_collection.find_one({"user_id": member.id, "guild_id": member.guild.id})
            if data and "roles" in data:
                roles_a_remettre = []
                for role_id in data["roles"]:
                    role = member.guild.get_role(role_id)
                    # On évite de redonner @everyone ou des rôles gérés par des intégrations/bots
                    if role and not role.managed and role != member.guild.default_role:
                        roles_a_remettre.append(role)
                
                if roles_a_remettre:
                    try:
                        await member.add_roles(*roles_a_remettre, reason="Restauration des rôles après un retour")
                    except Exception as e:
                        print(f"Erreur lors de la restauration des rôles : {e}")
                
                # Nettoyer la base de données une fois les rôles restitués
                self.left_roles_collection.delete_one({"user_id": member.id, "guild_id": member.guild.id})

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        # Sauvegarder les rôles du membre avant qu'il ne quitte (on exclut @everyone)
        if self.left_roles_collection is not None:
            roles_ids = [role.id for role in member.roles if role != member.guild.default_role and not role.managed]
            
            self.left_roles_collection.update_one(
                {"user_id": member.id, "guild_id": member.guild.id},
                {"$set": {"roles": roles_ids}},
                upsert=True
            )

async def setup(bot):
    await bot.add_cog(AutoRole(bot))