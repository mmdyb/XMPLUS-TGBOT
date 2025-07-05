# Author: Mmdyb
# GitHub: https://github.com/mmdyb/XMPLUS-TGBOT

from pyrogram import *
import pyromod
import sys

from data import Env
from modules.logger import log


env = Env()
bot = Client(
    "XMPLUS-TGBOT",
    api_id=env.API_ID, 
    api_hash=env.API_HASH, 
    bot_token=env.BOT_TOKEN,
    plugins=dict(root="modules")
)

if __name__ == "__main__":
    try:
        log.info("🟢 BOT is running...")
        bot.run()
        log.info("🔴 BOT is down!")
    except KeyboardInterrupt: # ctrl + c
        sys.exit()