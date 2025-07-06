# Author: Mmdyb
# GitHub: https://github.com/mmdyb/XMPLUS-TGBOT

from pyrogram import *
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, User, CallbackQuery, ChatPermissions
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.raw import *

from pyromod.config import config
config.disable_startup_logs = True
import pyromod

from datetime import datetime, timedelta, date
from time import *
import time as timee
import jdatetime
import math

import random
import string
import json
import os

import asyncio
import threading

from data import *
from .logger import log
from .utils import *
from .xmplus import *


##################################### New user
def new_user(user, earn, refer):
    db = DB()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if user not in db.users['id']:
        if earn == 1:
            status = 'not earn'
        else:
            status = 'earn'
        if refer not in db.users['id']:
            refer = user
        db.users['id'][user] = {
            "join_date": date,
            "refer": status,
            "referby": refer
        }
        db.users['total'] += 1
        db.save_users()

CHANNEL_MEMBER = [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]

##################################### Requirements
async def user_status(_, c, m):
    try:
        user_id = m.chat.id
    except:
        user_id = m.from_user.id
    
    if user_id == Env().OWNER:
        return True
    
    user = str(user_id)
    db = DB()
    earn = 0
    refer = user
    new_user(user, earn, refer)
    x = 0 # For multi channel support
    channel = db.settings['channel']
    if len(channel) == 0:
        return True
    try:
        member = await c.get_chat_member(channel, user)
        if member.status not in CHANNEL_MEMBER:
            return False
        # await referred(user, c)
        return True
    except:
        x += 1
        try:
            chat = await c.get_chat(channel)
            mention = chat.title
        except:
            mention = f"عضویت در کانال {x}"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(mention, url=f"https://t.me/{channel}")],
            [InlineKeyboardButton("عضو شدم ✅", callback_data="START")]
        ])
        await c.send_message(user_id, JOINING_TXT, reply_markup=markup)
        return False
user_status_filter = filters.create(user_status)

##################################### Owner filter
async def owner(_, c, m):
    user_id = m.from_user.id
    if user_id != Env().OWNER:
        return False
    return True
owner_filter = filters.create(owner)

##################################### Owner filter
async def setup(_, c, m):
    user_id = m.from_user.id
    db = DB()
    if (
        'channel' in db.settings and
        'order_channel' in db.settings and
        'panel_email' in db.settings and
        'panel_password' in db.settings and
        'test_package' in db.settings and
        'payment_card' in db.settings
    ):
        return True

    if user_id != Env().OWNER:
        await m.reply("**⚠️ ادمین هنوز رباتو تنظیم نکرده!**")
        return False

    if 'channel' not in db.settings:
        markup = ReplyKeyboardMarkup([
            [("بدون کانال")],
            [("لغو ❌")]
        ], resize_keyboard=True, one_time_keyboard=True)
        while True:
            try:
                ask = await c.ask(user_id, "لطفا آیدی کانال خود را ارسال کنید:\n\nمثال: `@channel`", reply_markup=markup, timeout=300)
                if not ask:
                    await ask.reply("**❌ تنظیم ربات لغو شد!**")
                    return False
                if ask.text == "لغو ❌":
                    await ask.reply("**❌ تنظیم ربات لغو شد!**")
                    return False
                elif ask.text == "بدون کانال":
                    db.settings['channel'] = ""
                else:
                    channel = ask.text.strip()
                    if not channel.startswith('@'):
                        await ask.reply("لطفا آیدی کانال را به صورت `@channel` ارسال کنید.")
                        continue
                    
                    try:
                        await c.get_chat_member(channel[1:], "me")
                    except:
                        await ask.reply("**❌ آیدی کانال اشتباهه یا ربات عضو کانال نیست!**")
                        log.error("❌ The channel is invalid or the bot has not been added to it!")
                        continue

                    db.settings['channel'] = channel[1:]
                db.save_settings()
                await ask.reply("کانال با موفقیت تنظیم شد✅")
                break
            except pyromod.exceptions.ListenerTimeout:
                await m.reply("**⚠️زمان شما به اتمام رسید!**")
                return False
    
    if 'order_channel' not in db.settings:
        while True:
            try:
                ask = await c.ask(user_id, "لطفا آیدی کانال سفارشات را ارسال کنید:\n\nمثال: `@channel`", reply_markup=CANCEL_MENU, timeout=300)
                if ask.text == "لغو ❌":
                    await ask.reply("**❌ تنظیم ربات لغو شد!**")
                    return False
                channel = ask.text.strip()
                if not channel.startswith('@'):
                    await ask.reply("لطفا آیدی کانال را به صورت `@channel` ارسال کنید.")
                    continue

                try:
                    await c.get_chat_member(channel[1:], "me")
                except:
                    await ask.reply("**❌ آیدی کانال سفارشات اشتباهه یا ربات عضو کانال نیست!**")
                    log.error("❌ The order channel is invalid or the bot has not been added to it!")
                    continue

                db.settings['order_channel'] = channel[1:]
                db.save_settings()
                await ask.reply("کانال سفارشات با موفقیت تنظیم شد✅")
                break
            except pyromod.exceptions.ListenerTimeout:
                await m.reply("**⚠️زمان شما به اتمام رسید!**")
                return False

    if 'panel_email' not in db.settings:
        while True:
            try:
                ask = await c.ask(user_id, "لطفا ایمیل پنل را ارسال کنید:", reply_markup=CANCEL_MENU, timeout=300)
                if ask.text == "لغو ❌":
                    await ask.reply("**❌ تنظیم ربات لغو شد!**")
                    return False
                email = ask.text.strip()
                db.settings['panel_email'] = email
                db.save_settings()
                await ask.reply("ایمیل پنل با موفقیت تنظیم شد✅")
                break
            except pyromod.exceptions.ListenerTimeout:
                await m.reply("**⚠️زمان شما به اتمام رسید!**")
                return False

    if 'panel_password' not in db.settings:
        while True:
            try:
                ask = await c.ask(user_id, "لطفا رمز عبور پنل را ارسال کنید:", reply_markup=CANCEL_MENU, timeout=300)
                if ask.text == "لغو ❌":
                    await ask.reply("**❌ تنظیم ربات لغو شد!**")
                    return False
                password = ask.text.strip()
                db.settings['panel_password'] = password
                db.save_settings()
                await ask.reply("رمز عبور پنل با موفقیت تنظیم شد✅")
                break
            except pyromod.exceptions.ListenerTimeout:
                await m.reply("**⚠️زمان شما به اتمام رسید!**")
                return False

    if 'test_package' not in db.settings:
        xm = XMPlus()
        while True:
            try:
                ask = await c.ask(user_id, "لطفا آیدی پکیج تست را ارسال کنید:", reply_markup=CANCEL_MENU, timeout=300)
                if ask.text == "لغو ❌":
                    await ask.reply("**❌ تنظیم ربات لغو شد!**")
                    return False
                package = await xm.getPackage(ask.text)
                if not package:
                    await m.reply("**⚠️ ایدی پکیج اشتباه است!**")
                    continue

                db.settings['test_package'] = ask.text
                db.save_settings()
                await ask.reply("آیدی پکیج با موفقیت تنظیم شد✅")
                break
            except pyromod.exceptions.ListenerTimeout:
                await m.reply("**⚠️زمان شما به اتمام رسید!**")
                return False

    if 'payment_card' not in db.settings:
        db.settings['payment_card'] = {}
        while True:
            try:
                ask = await c.ask(user_id, "لطفا شماره کارت بانکی را ارسال کنید:", reply_markup=CANCEL_MENU, timeout=300)
                if ask.text == "لغو ❌":
                    await ask.reply("**❌ تنظیم ربات لغو شد!**")
                    return False
                break
            except:
                await m.reply("**⚠️زمان شما به اتمام رسید!**")
                return False
        
        while True:
            try:
                ask2 = await c.ask(user_id, "لطفا نام صاحب کارت را ارسال کنید:", reply_markup=CANCEL_MENU, timeout=300)
                if ask2.text == "لغو ❌":
                    await ask2.reply("**❌ تنظیم ربات لغو شد!**")
                    return False

                break
            except pyromod.exceptions.ListenerTimeout:
                await m.reply("**⚠️زمان شما به اتمام رسید!**")
                return False
        
        db.settings['payment_card']['card_number'] = ask.text
        db.settings['payment_card']['card_name'] = ask2.text
        db.save_settings()
        await m.reply("مشخصات حساب بانکی با موفقیت تنظیم شد✅")

    return True
setup_filter = filters.create(setup)

##################################### MENU
async def menu(m, type, reply=True):
    if type == 'main':
        text = MENU_TXT
        markup = MENU
    elif type == 'm-wait':
        text = "⏳"
        markup = MENU
    if reply:
        return await m.reply(text, reply_markup=markup, reply_to_message_id=m.id)
    return await m.reply(text, reply_markup=markup)

##################################### Order id generator
def order_id_gen():
    timestamp = str(int(timee.time() * 1000))[-6:]
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    order_id = f"{timestamp}{random_str}"
    return order_id

##################################### Order Limit
def order_spam(user):
    db = DB()
    env = Env()
    not_paid_orders = []
    for order_id, order_info in db.orders.items():
        if "user_id" in order_info:
            if order_info.get("user_id") == user and order_info.get("status") == "NOT_PAID":
                created_at_str = order_info.get("created_at")
                if created_at_str:
                    try:
                        created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        created_at = datetime.min
                else:
                    created_at = datetime.min
                not_paid_orders.append((order_id, created_at))

    if len(not_paid_orders) >= env.ORDER_LIMIT:
        not_paid_orders.sort(key=lambda x: x[1])
        orders_to_delete = not_paid_orders[:len(not_paid_orders) - 9]
        for order_id, _ in orders_to_delete:
            del db.orders[order_id]
            db.save_orders()

##################################### Price Formater
def Amo(amo):
    pattern = '{:,.0f}'.format(int(amo)).replace(',', ',')
    return pattern

#####################################
def genUsername(user_id):
    user = str(user_id)
    db = DB()
    if "totalsub" not in db.users['id'][user]:
        db.users['id'][user]['totalsub'] = 0
    db.users['id'][user]["totalsub"] += 1
    total_sub = db.users['id'][user]['totalsub']
    db.save_users()
    username = f"{user_id}-{str(total_sub).zfill(2)}"
    return username

##################################### START
@Client.on_message(filters.command("start") & filters.private & setup_filter)
async def cmdStart(c, m):
    user_id = m.chat.id
    user = str(user_id)
    #### Start command
    if m.text == "/start":
        earn = 0
        refer = user
        new_user(user, earn, refer)
        print(f"{user} STARTED")
    elif len(m.command) > 1:
        #### Start command for referred
        if m.command[1].startswith('ref-'):
            refid = m.text.split()[1][4:]
            earn = 1
            refer = refid
            new_user(user, earn, refer)
            print(f"{user} REFERRED BY {refid}")
    else:
        earn = 0
        refer = user
        new_user(user, earn, refer)
    
    if await user_status_filter(c, m):
        await menu(m, 'main')

##################################### Cancel or back
@Client.on_message(filters.regex('بازگشت ↩️|BACK ↩️|منو اصلی ↩️|لغو ❌|انصراف ❌') & user_status_filter & setup_filter)
async def main_menu(c, m):
    await menu(m, 'main')

##################################### Account
@Client.on_message(filters.regex("حساب 👤") & user_status_filter)
async def account(c, m):
    user_id = m.from_user.id
    db = DB()
    xm = XMPlus()
    await c.send_chat_action(user_id, enums.ChatAction.PLAYING)

    if 'balance' not in db.users['id'][str(user_id)]:
        db.users['id'][str(user_id)]['balance'] = 0
    bal = f"""<b>{Amo(db.users['id'][str(user_id)]['balance'])}</b> تومان"""

    async def get_services():
        user_services = await xm.getUserServices(str(user_id))
        if not user_services:
            return None
        return len(user_services)

    async def get_join_date():
        dt_join = datetime.strptime(db.users['id'][str(user_id)]['join_date'], '%Y-%m-%d %H:%M:%S')
        jdt = jdatetime.datetime.fromgregorian(datetime=dt_join)
        return f"{jdt.year}/{str(jdt.month).zfill(2)}/{str(jdt.day).zfill(2)}"

    services_task = asyncio.create_task(get_services())
    join_date_task = asyncio.create_task(get_join_date())

    subs, join_date = await asyncio.gather(services_task, join_date_task)

    if subs is None:
        await m.reply("❌ خطا!")
        log.error("❌ Failed to get user services!")
        return 

    text = (
        f'👤 نام: **{m.from_user.first_name}**\n'
        f'💰 موجودی: {bal}\n'
        f'🛍 اشتراک ها: {subs}\n'
        f'\u200F➖➖➖➖➖➖➖➖\n'
        f'🏷️ شناسه: `{user_id}`\n'
        f'📆 عضویت: {join_date}'
    )

    await m.reply(text, reply_to_message_id=m.id, reply_markup=INCREASE_BAL)

##################################### Ticket
async def ticket_work(c, m):
    chat_id = m.chat.id
    db = DB()
    env = Env()
    user = str(m.from_user.id)

    try:
        answer = await m.chat.ask(
            "📩 پیام خود را با رعایت ادب برای پشتیبانی ارسال کنید :",
            reply_to_message_id=m.id,
            reply_markup=BACK_MENU,
            timeout=300
        )
        await c.send_chat_action(chat_id=chat_id, action=enums.ChatAction.SPEAKING)

        if answer.text == "بازگشت ↩️":
            await menu(answer, 'main')
            return
        
        userm = await c.get_users(answer.from_user.id)
        mention = userm.mention()
        TICKET_BUTTON = InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ پاسخ ✏️", callback_data=f"ANSWER_{chat_id}_msgid_{answer.id}")]
        ])
        if answer.text:
            await c.send_message(
                chat_id=env.OWNER,
                text=f"✉️ #TICKET: \n\n**{answer.text}** \n\n👤 ایدی: {mention}\n🏷️ شناسه: `{answer.from_user.id}`",
                reply_markup=TICKET_BUTTON
            )
            await m.reply(
                f"✅ پیام شما برای پشتیبانی ارسال شد: \n\n**{answer.text}**",
                reply_to_message_id=answer.id,
                reply_markup=MENU
            )
        
        elif answer.photo:
            if answer.caption == None:
                caption = f": \n\n**{answer.caption}**"
            await c.send_photo(
                env.OWNER, answer.photo.file_id,
                f"✉️ #TICKET{caption} \n\n👤 ایدی: {mention}\n🏷️ شناسه: `{answer.from_user.id}`",
                reply_markup=TICKET_BUTTON
            )
            await c.send_photo(
                chat_id,
                answer.photo.file_id,
                caption=f"✅ پیام شما برای پشتیبانی ارسال شد{caption}",
                reply_to_message_id=answer.id,
                reply_markup=MENU
            )
        
        elif answer.voice:
            await c.send_voice(
                chat_id=env.OWNER,
                voice=answer.voice.file_id,
                caption=f"✉️ #TICKET: \n\n👤 ایدی: {mention}\n🏷️ شناسه: `{answer.from_user.id}`",
                reply_markup=TICKET_BUTTON
            )
            await c.send_voice(
                chat_id,
                voice=answer.voice.file_id,
                caption=f"✅ پیام شما برای پشتیبانی ارسال شد",
                reply_to_message_id=answer.id,
                reply_markup=MENU
            )
        
        db.users['ticket_cooldown'][user] = str(m.date)
        db.save_users()
    except pyromod.exceptions.ListenerTimeout:
        await m.reply("**⚠️ زمان شما به اتمام رسید!**", reply_markup=MENU)
    except Exception as err:
        await m.reply("❌ خطا!", reply_markup=MENU)
        log.error(err)

@Client.on_message(filters.regex("پشتیبانی 👨‍💻") & user_status_filter)
async def contact_support(c, m):
    db = DB()
    user_id = m.from_user.id
    user = str(user_id)
    msg_date_str = str(m.date)
    if user in db.users['ticket_cooldown']:
        delta_msg_date = datetime.strptime(msg_date_str, '%Y-%m-%d %H:%M:%S')
        calc_time = delta_msg_date - timedelta(minutes=1) # hours minutes seconds
        new_msg_date = calc_time.strftime('%Y-%m-%d %H:%M:%S')
        user_date = db.users['ticket_cooldown'][user]
        if new_msg_date >= user_date:
            await ticket_work(c, m)
            return
        text = f"⚠ در هر دقیقه یک تیکت میتونید ارسال کنید..."
        await m.reply(text, reply_to_message_id=m.id)
        return
    await ticket_work(c, m)

##################################### Order Subscriptions
@Client.on_message(filters.regex("خرید اشتراک 🛍") & user_status_filter)
async def orderSub(c, m):
    xm = XMPlus()
    packages = await xm.getPackages()
    if not packages:
        await m.reply("**❌ خطا!**")
        log.error("❌ Failed to fetch packages!")
        return
    inline_keyboard = []
    for package in packages:
        if package.get("status") == 0:
            continue
        inline_keyboard.append([InlineKeyboardButton(f"{package.get('bandwidth')}", callback_data=f"select_package_{package.get('id')}")])
    markup = InlineKeyboardMarkup(inline_keyboard)
    bot = await c.get_me()
    await m.reply(f"**🛍 انتخاب نوع محصول:**\n\n➖➖➖➖➖➖\n🚀 @{bot.username}", reply_markup=markup, reply_to_message_id=m.id)

##################################### Test Subscriptions
@Client.on_message(filters.regex("تست ⚡️") & user_status_filter)
async def test_service(c, m):
    user_id = m.from_user.id
    db = DB()
    await c.send_chat_action(user_id, enums.ChatAction.PLAYING)

    if str(user_id) in db.users['test_subscription']:
        await m.reply("**⚠️ شما قبلا از اشتراک تست استفاده کردید**", reply_to_message_id=m.id)
        return
    
    xm = XMPlus()
    test_package = db.settings['test_package']
    package = await xm.getPackage(test_package)
    if not package:
        await m.reply("❌ خطا!")
        log.error("❌ Invalid test package id!")
        return
    
    addService = await xm.addService("custom", 1, test_package, f"{user_id}-TEST")
    if not addService:
        await m.reply("❌ خطا!")
        return
    
    config = await xm.getConfig(addService['serviceid'])
    if not config:
        await m.reply("❌ خطا!")
        log.error("❌ Failed to get config!")
        return
    await m.reply(f"**⚡️ اشتراک تست**\n\n{config}")
    
    db.users['test_subscription'][str(user_id)] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.save_users()

##################################### Subscriptions Menu generator
async def sub_status_list(user, page_number, type):
    env = Env()
    xm = XMPlus()

    services = await xm.getUserServices(user)
    if services is None:
        log.error("❌ Failed to get user services!")
        return None
    
    if len(services) == 0:
        return 0

    inline_keyboard = []
    inline_keyboard.append([InlineKeyboardButton("• لیست اشتراک ها •", callback_data="noop"),])
    
    start = env.SUB_STATUS_ITEM_LIST * (page_number - 1)
    end = env.SUB_STATUS_ITEM_LIST * page_number
    for sid, name in list(services.items())[start:end]:
        if type == "status":
            callback_type = f"sub_status-{sid}"
        elif type == "renew":
            callback_type = f"renewsub_{sid}"
        
        inline_keyboard.append([
            InlineKeyboardButton(name, callback_data=callback_type)
        ])
    
    total_pages = math.ceil(len(services) / env.SUB_STATUS_ITEM_LIST)
    buttons = []
    if page_number > 1:
        buttons.append(InlineKeyboardButton("◀️", callback_data=f"list_sub_status-{user}-{page_number - 1}-{type}"))
    if total_pages > 1:
        buttons.append(InlineKeyboardButton(f"({page_number}/{total_pages})", callback_data="noop"))
    if page_number < total_pages:
        buttons.append(InlineKeyboardButton("▶️", callback_data=f"list_sub_status-{user}-{page_number + 1}-{type}"))
    inline_keyboard.append(buttons)

    markup = InlineKeyboardMarkup(inline_keyboard)
    return markup

##################################### Subscriptions Menu
@Client.on_message(filters.regex("اشتراک های من 🚀") & user_status_filter)
async def subscription_status(c, m):
    user_id = m.chat.id

    await c.send_chat_action(user_id, enums.ChatAction.PLAYING)
    waiting = await m.reply('⏳', reply_to_message_id=m.id)

    markup = await sub_status_list(str(user_id), 1, "status")
    if markup is None:
        await m.reply("❌ خطا!")
        return
    
    if markup == 0:
        await waiting.edit_text("❌ شما اشتراک فعالی ندارید")
        return
    
    bot = await c.get_me()
    await waiting.edit_text(f"**یکی از اشتراک های زیر را انتخاب کنید:**\n\n➖➖➖➖➖➖\n🚀 @{bot.username}", reply_markup=markup)

##################################### CallbackQuery
@Client.on_callback_query(user_status_filter)
async def CallBackStartUpdate(c, cq):
    m = cq.message
    user_id = cq.from_user.id
    env = Env()
    db = DB()
    xm = XMPlus()
    
    if cq.data == "START":
        await c.answer_callback_query(cq.id, "عضو شدی 🥳")
        await m.delete()
        await menu(m, 'main')

    ##################################### (TICKET)

    elif cq.data.startswith("ANSWER_"):
        key_start = cq.data.find("ANSWER_") + len("ANSWER_")
        chat_id = cq.data[key_start : cq.data.find("_", key_start)]

        msgid_key = cq.data.find("msgid_") + len("msgid_")
        msg_id = int(cq.data[msgid_key:])

        ask = await m.chat.ask(f"✏ پاسخ تیکت را ارسال کنید:", reply_to_message_id=m.id, reply_markup=BACK_MENU)
        if ask.text == "بازگشت ↩️":
            await menu(ask, 'main')
            return
        
        if ask.text:
            await c.send_message(chat_id, f"🔔 پاسخ پشتیبانی:\n\n**{ask.text}**", reply_to_message_id=msg_id)
        
        elif ask.photo:
            if ask.caption:
                caption = f":\n\n**{ask.caption}**"
            await c.send_photo(chat_id, ask.photo.file_id, f"🔔 پاسخ پشتیبانی{caption}", reply_to_message_id=msg_id)
        
        elif ask.voice:
            if ask.caption:
                caption = f":\n\n**{ask.caption}**"
            await c.send_voice(chat_id, voice=ask.voice.file_id, caption=f"🔔 پاسخ پشتیبانی{caption}", reply_to_message_id=msg_id)
        
        await ask.reply("ارسال شد ✅", reply_markup=MENU, reply_to_message_id=ask.id)
        if str(chat_id) in db.users['ticket_cooldown']:
            del db.users['ticket_cooldown'][str(chat_id)]
        db.save_users()
    
    ##################################### (ORDER)

    elif cq.data.startswith("select_package_"):
        package_id = cq.data[15:]

        package = await xm.getPackage(package_id)
        if not package:
            await c.answer_callback_query(cq.id, "⚠️ سغارش شما دیگه موجود نیست!", show_alert=True)
            log.error("❌ Failed to fetch package!")
            return
        
        threading.Thread(
            target=order_spam,
            args=(str(user_id),)
        ).start()

        order_id = order_id_gen()
        db.orders[order_id] = {
            "order_type": "NEW_SUB",
            "user_id": str(user_id),
            "package_id": package_id,
            "status": "NOT_PAID",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        db.save_orders()

        inline_keyboard = []
        for key, value in package['price_option'].items():
            if key == "topup_traffic":
                continue
            if int(value['price']) <= 0:
                continue
            
            option = env.PRICE_OPTION.get(key, None)
            if not option:
                log.error(f"""❌ The price option "{option}" is not exist in env.PRICE_OPTION!""")
                continue

            inline_keyboard.append([InlineKeyboardButton(option, callback_data=f"order_service_{key}_{order_id}")])
        
        markup = InlineKeyboardMarkup(inline_keyboard)
        await m.edit_reply_markup(reply_markup=markup)

    elif cq.data.startswith("order_service_"):
        parts = cq.data.split('_')
        option = parts[2]
        order_id = parts[3]

        order = db.orders[order_id]
        await c.send_chat_action(user_id, enums.ChatAction.PLAYING)
        
        while True:
            try:
                service_name = await c.ask(user_id, "**✏️ اسم اشتراک را بفرستید:**", reply_markup=CANCEL_MENU, timeout=60)
                if hasattr(service_name, 'sent_message'):
                    await service_name.sent_message.delete()
                if hasattr(service_name, 'request'):
                    await service_name.request.delete()
                if not service_name:
                    return
                if service_name.text == "لغو ❌":
                    await service_name.reply("**❌ خرید شما لغو شد!**", reply_markup=MENU)
                    return
                if len(service_name.text) >= env.SUB_NAME_LIMIT:
                    await service_name.reply(f"**⚠️ اسم اشتراک شما بیش از **`{env.SUB_NAME_LIMIT}`** حرف است**", reply_markup=MENU)
                    continue
                break
            except pyromod.exceptions.ListenerTimeout:
                await m.reply("**⚠️ زمان شما به اتمام رسید!**", reply_markup=MENU)
                return
        
        await menu(m, "m-wait", False)
        
        package = await xm.getPackage(order['package_id'])
        if not package:
            await c.answer_callback_query(cq.id, "⚠️ سغارش شما دیگه موجود نیست!", show_alert=True)
            return

        order['price_option'] = option
        amo = int(package['price_option'][option]['price'])
        order['amo'] = amo
        order['service_name'] = service_name.text
        db.save_orders()

        text = f"""{package.get("name")}\n🔌 تعداد کاربر: {package.get("iplimit")}\n💲 مبلغ: <b>{Amo(amo)} تومان</b>\n🛍 شماره سفارش: ||{order_id}||\n\n↲<u>🏧 لطفا یک روش پرداخت را انتخاب کنید</u>"""
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("کیف پول 💰", callback_data=f"BALANCE_PAY-{order_id}")],
            [InlineKeyboardButton("کارت به کارت 💳", callback_data=f"CART_PAY-{order_id}")]
        ])
        await m.delete()
        try:
            await m.reply(text, reply_markup=markup)
        except:
            await c.answer_callback_query(cq.id, "❌ برای این پکیج هیج قیمتی تعریف نشده است!", show_alert=True)
    
    elif cq.data.startswith("BALANCE_PAY-"):
        await c.send_chat_action(user_id, enums.ChatAction.PLAYING)

        order_id = cq.data[12:]
        
        if order_id not in db.orders:
            await c.answer_callback_query(cq.id, "⚠️ سغارش دیگه موجود نیست!", show_alert=True)
            return
        
        order = db.orders[order_id]
        if order.get("status") != "NOT_PAID":
            await c.answer_callback_query(cq.id, "⚠️ این سفارش قبلا پرداخت شده است!", show_alert=True)
            return
        
        package = await xm.getPackage(order['package_id'])
        if not package:
            await c.answer_callback_query(cq.id, "⚠️ سغارش شما دیگه موجود نیست!", show_alert=True)
            return

        user = db.users['id'].get(str(user_id), {})
        bal = user.get('balance', 0)
        amo = int(order.get("amo"))
        if bal < amo:
            await c.answer_callback_query(cq.id, "⚠️ موجودی شما کافی نیست!", show_alert=True)
            return
        
        addService = await xm.addService(order['price_option'], 1, order['package_id'], genUsername(user_id))
        if not addService:
            await c.answer_callback_query(cq.id, "❌ خطا!", show_alert=True)
            return
        
        if order['user_id'] not in db.services:
            db.services[order['user_id']] = {}
        db.services[order['user_id']][addService['serviceid']] = order['service_name']
        db.save_services()

        user['balance'] -= amo
        order['status'] = "PAID"
        order['pay'] = "BALANCE"
        order['paid_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.save_users()
        db.save_orders()

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("پرداخت شده ✅", callback_data="order_purchased")]
        ])
        await m.edit_reply_markup(reply_markup=markup)

        await c.answer_callback_query(cq.id, "✅ پرداخت با موفقیت انجام شد", show_alert=True)
        config = await xm.getConfig(addService['serviceid'])
        if not config:
            await c.answer_callback_query(cq.id, "❌ خطا!", show_alert=True)
            return log.error("❌ Failed to get config!")
        await c.send_message(user_id, f"**پرداخت با موفقیت انجام شد ✅**\n\n{config}")
    
    elif cq.data.startswith("CART_PAY-"):
        await c.send_chat_action(user_id, enums.ChatAction.PLAYING)

        order_id = cq.data[9:]
        order = db.orders[str(order_id)]

        if order_id not in db.orders:
            await c.answer_callback_query(cq.id, "⚠️ سغارش دیگه موجود نیست!", show_alert=True)
            return

        if 'pay' in order:
            await c.answer_callback_query(cq.id, "⚠️ این سفارش قبلا پرداخت شده!", show_alert=True)
            return
        
        package = await xm.getPackage(order['package_id'])
        if not package:
            await c.answer_callback_query(cq.id, "⚠️ سغارش شما دیگه موجود نیست!", show_alert=True)
            return
        
        if 'order_channel' not in db.settings:
            await c.answer_callback_query(cq.id, "❌ خطا!", show_alert=True)
            return log.error("❌ The order channel is not set up!")
        
        try:
            await c.get_chat_member(db.settings['order_channel'], "me")
        except:
            await c.answer_callback_query(cq.id, "❌ خطا!", show_alert=True)
            return log.error("❌ The order channel is invalid or the bot has not been added to it!")
        
        answer = await m.chat.ask(f"""✔️ برای تکمیل سفارش مبلغ را به کارت واریز کنید و رسید را ارسال کنید\n\nکارت: <b><code>{db.settings['payment_card']['card_number']}</code></b>\nصاحب حساب: <b>{db.settings['payment_card']['card_name']}</b>""", reply_markup=CANCEL_MENU)
        if hasattr(answer, 'sent_message'):
            await answer.sent_message.delete()
        if hasattr(answer, 'request'):
            await answer.request.delete()
        
        
        
        if not answer.photo:
            if answer.text == "لغو ❌":
                await menu(answer, 'main')
                return
            
            await menu(answer, 'm-wait')
            await c.send_message(user_id, "🟣️ رسید فقط در قالب عکس رسیدگی میشه **(دوباره تلاش کنید)**\n⁉️ اگر از پرداخت خود رسید پشتیبانی شده ندارید با پشتیبانی ارتباط برقرار کنید.", reply_to_message_id=answer.id)
            return
        
        await m.reply(ORDER_WAITING_TEXT, reply_to_message_id=answer.id, reply_markup=MENU)
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("سفارش درخواست شد ✅", callback_data="order_requested")]
        ])
        await m.edit_reply_markup(reply_markup=markup)

        userm = await c.get_users(user_id)
        mention = userm.mention()
        t = [f"{package['name']}\n\n🛍 شماره سفارش: `{order_id}`\n💲 مبلغ: <b>{Amo(order['amo'])} تومان</b>\n📦 سفارش از طرف {mention}\n🏷 شناسه: <code>{answer.from_user.id}</code>"]
        if answer.caption != None:
            t.append(f"\n📜 متن:\n{answer.caption}")
        text = ''.join(t)
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌", callback_data=f"ORDER_DENY-{order_id}"), 
                InlineKeyboardButton("✅", callback_data=f"ORDER_CONFRIM-{order_id}")]
        ])

        await c.send_photo(db.settings['order_channel'], answer.photo.file_id,
                caption=text,
                reply_markup=markup)
        
        order['status'] = "PENDING"
        order['pay'] = "CARD"
        db.save_orders()
    
    elif cq.data.startswith("ORDER_DENY-"):
        order_id = cq.data[11:]
        if env.OWNER != user_id:
            return
        
        await c.answer_callback_query(cq.id, "❌")
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("رد شد ❌", callback_data="FAKE")]
        ])
        await m.edit_reply_markup(reply_markup=markup)

        order = db.orders[str(order_id)]
        package = await xm.getPackage(order['package_id'])
        order['status'] = "DENIED"
        db.save_orders()
        await c.send_message(order['user_id'], f"سفارش {package['name']}؛ **رد شد🚫**")
    
    elif cq.data.startswith("ORDER_CONFRIM-"):
        order_id = cq.data[14:]
        if env.OWNER != user_id:
            return
        
        order = db.orders[str(order_id)]
        if order.get("status") == "PAID":
            await c.answer_callback_query(cq.id, "⚠️ این سفارش قبلا پرداخت شده است!", show_alert=True)
            return
        
        await c.answer_callback_query(cq.id, "✅")
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("انجام شد ✅", callback_data="order_done")]
        ])
        await m.edit_reply_markup(reply_markup=markup)

        if order['order_type'] == "MEW_SUB":
            package = await xm.getPackage(order['package_id'])
            if not package:
                await c.answer_callback_query(cq.id, "⚠️ پکیج سفارش دیگه موجود نیست!", show_alert=True)
                return

            addService = await xm.addService(order['price_option'], 1, order['package_id'], genUsername(user_id))
            if not addService:
                await c.answer_callback_query(cq.id, "❌ خطا!", show_alert=True)
                return
            
            if order['user_id'] not in db.services:
                db.services[order['user_id']] = {}
            db.services[order['user_id']][[addService['serviceid']]] = order['service_name']
            db.save_services()

            config = await xm.getConfig(addService['serviceid'])
            if not config:
                await c.answer_callback_query(cq.id, "❌ خطا!", show_alert=True)
                log.error("❌ Failed to get config!")
                return
            
            text = f"**سفارش تایید شد✅**\n\n{config}"
        
        elif order['order_type'] == "INCREASE_BAL":
            amo = order['amo']
            db.users['id'][order['user_id']]['balance'] += amo

            text = f"**موجودی شما `{(Amo(amo))}` افزایش یافت.✅**"

        order['pay'] = "CARD"
        order['status'] = "PAID"
        order['paid_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.save_orders()
        await c.send_message(order['user_id'], text)
    
    elif cq.data == "INCREASE_BALANCE":
        while True:
            try:
                ask = await c.ask(user_id, "**💲 مبلع مورد نظر خود را به تومان وارد کنید:**", reply_markup=CANCEL_MENU, timeout=60)
                if ask.text == "لغو ❌":
                    await ask.reply("**❌ خرید شما لغو شد!**", reply_markup=MENU)
                    return
                try:
                    amo = int(ask.text)
                except ValueError:
                    if hasattr(ask, 'sent_message'):
                        await ask.sent_message.delete()
                    if hasattr(ask, 'request'):
                        await ask.request.delete()
                    await ask.reply("**⚠️ لطفا مبلغ را به عدد وارد کنید.**", reply_markup=MENU)
                    continue
                if amo < 1000:
                    if hasattr(ask, 'sent_message'):
                        await ask.sent_message.delete()
                    if hasattr(ask, 'request'):
                        await ask.request.delete()
                    await ask.reply(f"**⚠️ امکان انتخاب مبلغ کمتر از `{Amo(1000)}` نیست!**", reply_markup=MENU)
                    continue
                if amo > env.MAX_INCREASE_BAL:
                    if hasattr(ask, 'sent_message'):
                        await ask.sent_message.delete()
                    if hasattr(ask, 'request'):
                        await ask.request.delete()
                    await ask.reply(f"**⚠️ امکان انتخاب مبلغ بیشتر از `{Amo(env.MAX_INCREASE_BAL)}` نیست!**", reply_markup=MENU)
                    continue
                break
            except pyromod.exceptions.ListenerTimeout:
                await m.reply("**⚠️ زمان شما به اتمام رسید!**", reply_markup=MENU)
                return

            except Exception as err:
                await m.reply("❌ خطا!", reply_markup=MENU)
                log.error(err)
                return
        
        order_id = order_id_gen()
        db.orders[order_id] = {
            "order_type": "INCREASE_BAL",
            "user_id": str(user_id),
            "amo": int(amo),
            "status": "NOT_PAID",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db.save_orders()

        text = f"""💲 مبلغ افزایش موجودی: <b>{Amo(amo)} تومان</b>\n🛍 شماره سفارش: ||{order_id}||\n\n↲<u>🏧 لطفا یک روش پرداخت را انتخاب کنید</u>"""
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("کارت به کارت 💳", callback_data=f"INCREASE_BAL_CART_PAY-{order_id}")]
        ])
        await m.reply(text, reply_markup=markup)
    
    elif cq.data.startswith("INCREASE_BAL_CART_PAY-"):
        await c.send_chat_action(user_id, enums.ChatAction.PLAYING)

        order_id = cq.data[22:]
        order = db.orders[str(order_id)]

        if order_id not in db.orders:
            await c.answer_callback_query(cq.id, "⚠️ سغارش دیگه موجود نیست!", show_alert=True)
            return

        if 'pay' in order:
            await c.answer_callback_query(cq.id, "⚠️ این سفارش قبلا پرداخت شده!", show_alert=True)
            return

        answer = await m.chat.ask(f"""✔️ برای تکمیل سفارش مبلغ را به کارت واریز کنید و رسید را ارسال کنید\n\nکارت: <b><code>{db.settings['payment_card']['card_number']}</code></b>\nصاحب حساب: <b>{db.settings['payment_card']['card_name']}</b>""", reply_markup=CANCEL_MENU)
        if hasattr(answer, 'sent_message'):
            await answer.sent_message.delete()
        if hasattr(answer, 'request'):
            await answer.request.delete()
        
        if not answer.photo:
            if answer.text == "لغو ❌":
                await menu(answer, 'main')
                return
            
            await menu(answer, 'm-wait')
            await c.send_message(user_id, "🟣️ رسید فقط در قالب عکس رسیدگی میشه **(دوباره تلاش کنید)**\n⁉️ اگر از پرداخت خود رسید پشتیبانی شده ندارید با پشتیبانی ارتباط برقرار کنید.", reply_to_message_id=answer.id)
            return
        
        await m.reply(ORDER_WAITING_TEXT, reply_to_message_id=answer.id, reply_markup=MENU)
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("سفارش درخواست شد ✅", callback_data="order_requested")]
        ])
        await m.edit_reply_markup(reply_markup=markup)

        userm = await c.get_users(user_id)
        mention = userm.mention()
        t = [f"**💲 مبلغ افزایش موجودی:**{Amo(order['amo'])} تومان\n\n🛍 شماره سفارش: `{order_id}`\n📦 سفارش از طرف {mention}\n🏷 شناسه: <code>{answer.from_user.id}</code>"]
        if answer.caption != None:
            t.append(f"\n📜 متن:\n{answer.caption}")
        text = ''.join(t)
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌", callback_data=f"ORDER_DENY-{order_id}"), 
                InlineKeyboardButton("✅", callback_data=f"ORDER_CONFRIM-{order_id}")]
        ])

        await c.send_photo(db.settings['order_channel'], answer.photo.file_id,
                caption=text,
                reply_markup=markup)

        order['status'] = "PENDING"
        order['pay'] = "CARD"
        db.save_orders()

    ##################################### (SUB STATUS)

    elif cq.data.startswith("list_sub_status-"):
        split_data = cq.data.split('-')
        user = split_data[1]
        page_number = int(split_data[2])
        status = split_data[3]
        await c.send_chat_action(user_id, enums.ChatAction.PLAYING)
        markup = await sub_status_list(user, page_number, status)
        await m.edit_reply_markup(reply_markup=markup)

    elif cq.data.startswith("sub_status-"):
        await m.delete()
        await c.send_chat_action(user_id, enums.ChatAction.PLAYING)
        sid = cq.data[11:]
        for user, sids in db.services.items():
            for key, value in sids.items():
                if key == str(sid):
                    name = value
        markup = await xm.getServiceMarkup(sid)
        await m.reply(f"🚀 اشتراک (`{name}`)\n\n{await xm.getConfig(sid)}", reply_markup=markup)
    
    elif cq.data.startswith("status_update-"):
        await c.send_chat_action(user_id, enums.ChatAction.PLAYING)
        sid = cq.data[14:]
        markup = await xm.getServiceMarkup(sid)
        try:
            await m.edit_reply_markup(reply_markup=markup)
        except:
            pass
        await c.answer_callback_query(cq.id, "🔄 بروزرسانی")
    