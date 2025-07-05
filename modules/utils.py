# Author: Mmdyb
# GitHub: https://github.com/mmdyb/XMPLUS-TGBOT

from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


JOINING_TXT = "**برای فعال شدن ربات لطفا عضو کانال زیر شوید:**\n\n__🔰سپس دکمه عضو شدم را بزنید.__"

MENU_TXT = "🏠"

ORDER_WAITING_TEXT = "**⏳ سفارش شما به لیست اضافه شد، لطفا منتطر بررسی آن توسط ادمین باشید.**"

MENU = ReplyKeyboardMarkup([
    [("تست ⚡️"), ("خرید اشتراک 🛍")],
    [("حساب 👤"), ("اشتراک های من 🚀")],
    [("پشتیبانی 👨‍💻")]
], resize_keyboard=True)

INCREASE_BAL = InlineKeyboardMarkup([
    [InlineKeyboardButton("افزایش موجودی 💰", callback_data=f"INCREASE_BALANCE")]
])

CANCEL_MENU = ReplyKeyboardMarkup([
    [("لغو ❌")]
], resize_keyboard=True, one_time_keyboard=True)

BACK_MENU = ReplyKeyboardMarkup([
    [("بازگشت ↩️")]
    ], resize_keyboard=True, one_time_keyboard=True)