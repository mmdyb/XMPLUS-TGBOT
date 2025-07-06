# Author: Mmdyb
# GitHub: https://github.com/mmdyb/XMPLUS-TGBOT

from decouple import config
import json
import os


# Environment
class Env:
    def __init__(self):
        self.config_path = '.env'
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Environment file not found at {self.config_path}")
        
        self.API_ID = config("API_ID", cast=int)
        self.API_HASH = config("API_HASH", cast=str)
        self.BOT_TOKEN = config("BOT_TOKEN", cast=str)
        self.OWNER = config("OWNER", cast=int)
        self.API_URL = config("API_URL", cast=str)
        self.MAX_RETRIES = config("MAX_RETRIES", cast=int, default=3) # do not change it less than 2
        self.ORDER_LIMIT = config(
            "ORDER_LIMIT",
            cast=int,
            default=3
        )
        self.SUB_NAME_LIMIT = config(
            "SUB_NAME_LIMIT",
            cast=int,
            default=20
        )
        self.MAX_INCREASE_BAL = config(
            "MAX_INCREASE_BAL", cast=int, default=10000000
        )
        self.SUB_STATUS_ITEM_LIST = config(
            "SUB_STATUS_ITEM_LIST", cast=int, default=5
        )
        self.PRICE_OPTION = {'month': 'ماهانه', 'quater': 'سه ماهه', 'semiannual': 'شش ماهه', 'annual': 'سالانه'}

# Database
class DB:
    def __init__(self):
        self.settings_path = './data/db/settings.json'
        self.users_path = './data/db/users.json'
        self.orders_path = './data/db/orders.json'
        self.services_path = './data/db/services.json'

        self.settings = self.load(self.settings_path)
        self.users = self.load(self.users_path)
        self.orders = self.load(self.orders_path)
        self.services = self.load(self.services_path)

    def load(self, path):
        if not os.path.exists(path):
            return {}
        with open(path, 'r') as f:
            return json.load(f)

    def save(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
            
    def save_settings(self):
        self.save(self.settings_path, self.settings)
    def save_users(self):
        self.save(self.users_path, self.users)
    def save_orders(self):
        self.save(self.orders_path, self.orders)
    def save_services(self):
        self.save(self.services_path, self.services)