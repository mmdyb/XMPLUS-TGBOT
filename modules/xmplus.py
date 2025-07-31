# Author: Mmdyb
# GitHub: https://github.com/mmdyb/XMPLUS-TGBOT

import asyncio
import httpx
import html
from datetime import datetime
from time import *
import jdatetime

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from data import *
from .logger import log


class XMPlus:
    token = None

    def __init__(self):
        self.client = httpx.AsyncClient()
        self.client.headers["Content-Type"] = "application/json"
        self.client.headers["Authorization"] = f"Bearer {XMPlus.token}"

        self.db = DB()
        self.env = Env()
        
        self.api_url = self.env.API_URL
        self.panel_email = self.db.settings['panel_email']
        self.panel_password = self.db.settings['panel_password']
        
        self.token_api = f"{self.api_url}/api/reseller/token"
        self.getPackages_api = f"{self.api_url}/api/reseller/packages"
        self.addService_api = f"{self.api_url}/api/reseller/service/add"
        self.renewService_api = f"{self.api_url}/api/reseller/service/renew"
        self.getServices_api = f"{self.api_url}/api/reseller/services"
        self.getService_api = f"{self.api_url}/api/reseller/service/info"
    
    async def login(self):
        del self.client.headers["Authorization"]
        log.info("🔄 Attempting to log in to the panel.")
        data = {
            "email": self.panel_email,
            "passwd": self.panel_password
        }
        res = await self.client.post(self.token_api, json=data)
        
        try:
            json_data = res.json()
        except ValueError:
            log.error(f"❌ Login response is not valid JSON!")
            log.debug(f"🔍 Login API response text:\n{html.escape(res.text[:500])}")
            return None

        if res.status_code == 200 and json_data.get("status") == "success":
            XMPlus.token = json_data.get("data", {}).get("token")
            self.client.headers["Authorization"] = f"Bearer {XMPlus.token}"
            log.info("✅ Login to the panel is successful.")
            return XMPlus.token

        log.error(f"❌ Login failed! Response: {html.escape(res.text[:500])}")
        return None

    async def req(self, method, url, status, **kwargs):
        logged_in = False
        attempt = 0
        while attempt < self.env.MAX_RETRIES:
            attempt += 1
            try:
                res = await self.client.request(method, url, **kwargs)
                # print(f"Attempt {attempt}: {method} {url} -> {res.status_code}")
                # print(res.text)
                if res.status_code == 200 and res.json().get("status") == status:
                    return res
            except ValueError:
                log.error("❌ Response is not valid JSON!")
            except Exception as err:
                log.error(err)

            if not logged_in:
                logged_in = await self.login()
                if logged_in:
                    continue
            break
        # words = res.text.split()
        # short_text = ' '.join(words[:10]) + ('...' if len(words) > 10 else '')
        # escaped_text = html.escape(short_text)
        log.critical(f"🛑 Request to API failed — (status {res.status_code}):\n{html.escape(res.text[:500])}")
        return None
    
    async def getPackages(self):
        res = await self.req('POST', self.getPackages_api, "success")
        if not res:
            log.error("❌ Failed to get packages!")
            return None
        return res.json().get("packages")
    
    async def getPackage(self, package_id):
        packages = await self.getPackages()
        if not packages:
            return None
        for package in packages:
            if package.get("id") == int(package_id):
                return package
        return None
    
    async def addService(self, cycle, qty, package_id, remarks):
        data = {
            "cycle": cycle,
            "qty": qty,
            "packageid": package_id,
            "remarks": remarks
        }
        
        res = await self.req('POST', self.addService_api, "success", json=data)
        if not res:
            log.error("❌ Failed to add service!")
            return None
        return res.json()

    async def renewService(self, sid):
        data = {
            "serviceid": sid
        }
        res = await self.req('POST', self.renewService_api, "success", json=data)
        if not res:
            log.error("❌ Failed to renew service!")
            return None
        return res.json()

    # async def getServices(self):
    #     res = await self.req('POST', self.getServices_api, "success")
    #     if not res:
    #         log.error("❌ Failed to get services!")
    #         return None
    #     return res.json().get("services")

    async def getService(self, sid):
        data = {
            "serviceid": int(sid)
        }
        res = await self.req('POST', self.getService_api, "فعال", json=data)
        if not res:
            log.error("❌ Failed to get service!")
            return None
        return res.json()

    async def getUserServices(self, user_id):
        user_services = {}
        if str(user_id) not in self.db.services:
                self.db.services[str(user_id)] = {}
        for sid in self.db.services[str(user_id)]:
            service = await self.getService(int(sid))
            if service:
                # user_services.update(service)
                user_services.update({sid: self.db.services[str(user_id)][sid]})
        return user_services
    
    async def getConfig(self, sid):
        service = await self.getService(sid)
        if not service:
            return None
        
        subLink = service.get('sublink', None)
        config = service['servers'][0]['uri']
        
        return f"**🔰 لینک اشتراک:**\n`{subLink}`\n\n**🔰 کانفیگ:**\n`{config}`"
    
    async def getServiceMarkup(self, sid):
        service = await self.getService(sid)
        if not service:
            return None
        
        total_quota = service.get('traffic', "-")
        traffic_used = service.get('used_traffic', "-")
        iplimit = service.get('iplimit', "-")
        option = self.env.PRICE_OPTION.get(service['billing'], "-")

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{total_quota}", callback_data="FAKE"),
            InlineKeyboardButton("🔋 کل ترافیک:", callback_data="FAKE")],

            [InlineKeyboardButton(f"{traffic_used}", callback_data="FAKE"),InlineKeyboardButton("🚦 ترافیک مصرف شده:", callback_data="FAKE")],

            [InlineKeyboardButton(f"{iplimit}", callback_data="FAKE"), InlineKeyboardButton("🔌 محدودیت اتصال:", callback_data="FAKE")],
            [InlineKeyboardButton(f"{option}", callback_data="FAKE"), InlineKeyboardButton("⏳ مهلت اشتراک:", callback_data="FAKE")],

            [InlineKeyboardButton("بروزرسانی", callback_data=f"status_update-{sid}")]
        ])
