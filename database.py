import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["lego_bot_db"]

coins_collection = db["coins"]
coupons_collection = db["coupons"]

# --- Fonctions pour les Coins ---
def get_user_coins(user_id: int) -> int:
    user_data = coins_collection.find_one({"user_id": user_id})
    return user_data["coins"] if user_data else 0

def update_user_coins(user_id: int, amount: int) -> int:
    # Récupère le solde actuel, ajoute le montant, et met à jour
    user_data = coins_collection.find_one({"user_id": user_id})
    current_coins = user_data["coins"] if user_data else 0
    new_total = current_coins + amount

    coins_collection.update_one(
        {"user_id": user_id},
        {"$set": {"coins": new_total}},
        upsert=True
    )
    return new_total

# --- Fonctions pour les Coupons ---
def save_user_coupon(user_id: int, coupon_code: str, percentage: int):
    coupons_collection.insert_one({
        "user_id": user_id,
        "code": coupon_code.upper(),
        "Percentage": percentage
    })

def remove_coupon_from_db(coupon_code: str):
    coupon = coupons_collection.find_one_and_delete({"code": coupon_code.upper()})
    if coupon:
        return coupon["user_id"], coupon["Percentage"]
    return None, None