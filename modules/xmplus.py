# Author: Mmdyb
# GitHub: https://github.com/mmdyb/XMPLUS-TGBOT

import asyncio
import httpx

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from data import *
from .logger import log


class XMPlus:
    client = httpx.AsyncClient()
    client.headers = {
        "Content-Type": "application/json"
    }

    token = None

    def __init__(self):
        self.db = DB()
        self.env = Env()
        
        self.panel_email = self.db.settings['panel_email']
        self.panel_password = self.db.settings['panel_password']
        self.api_url = "https://anonverse.net"
        self.token_api = f"{self.api_url}/api/reseller/token"
        self.getPackages_api = f"{self.api_url}/api/reseller/packages"
        self.addService_api = f"{self.api_url}/api/reseller/service/add"
        self.getServices_api = f"{self.api_url}/api/reseller/services"
        self.getService_api = f"{self.api_url}/api/reseller/service/info"
    
    async def login(self):
        log.info("🔄 Attempting to log in to the panel.")
        data = {
            "email": self.panel_email,
            "passwd": self.panel_password
        }
        res = await XMPlus.client.post(self.token_api, json=data)
        if res.status_code == 200 and res.json().get("status") == "success":
            XMPlus.token = res.json().get("data").get("token")
            XMPlus.client.headers["Authorization"] = f"Bearer {XMPlus.token}"
            log.info("✅ Login to the panel is successful.")
            return XMPlus.token
        
        log.error("❌ Unable to log in to the panel!")
        return None

    async def req(self, method, url, status, **kwargs):
        logged_in = False
        attempt = 0
        retries = 2
        while attempt < retries:
            attempt += 1
            try:
                res = await XMPlus.client.request(method, url, **kwargs)
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
        log.critical(f"🛑 Request to API failed — (status {res.status_code}):\n{res.text}")
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

    async def getServices(self):
        res = await self.req('POST', self.getServices_api, "success")
        if not res:
            log.error("❌ Failed to get services!")
            return None
        return res.json().get("services")

    async def getService(self, sid):
        data = {
            "serviceid": sid
        }
        res = await self.req('POST', self.getService_api, "فعال", json=data)
        if not res:
            log.error("❌ Failed to get service!")
            return None
        return res.json()

    async def getUserServices(self, user_id):
        services = await self.getServices()
        if not services:
            return None
        
        user_services = {}

        # for sid in services:
        #     service = await self.getService(sid['sid'])
        #     if service and service.get("remarks", "").startswith(user_id):
        #         user_services.update(service)

        all_sids = [service['sid'] for service in services]
        if str(user_id) not in self.db.services:
                self.db.services[str(user_id)] = {}
        for sid in self.db.services[str(user_id)]:
            if int(sid) in all_sids:
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

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{total_quota}", callback_data="FAKE"),
            InlineKeyboardButton("🔋 کل ترافیک:", callback_data="FAKE")],

            [InlineKeyboardButton(f"{traffic_used}", callback_data="FAKE"),InlineKeyboardButton("🚦 ترافیک مصرف شده:", callback_data="FAKE")],

            [InlineKeyboardButton(f"{iplimit}", callback_data="FAKE"), InlineKeyboardButton("🔌 محدودیت اتصال:", callback_data="FAKE")],

            [InlineKeyboardButton("بروزرسانی", callback_data=f"status_update-{sid}")]
        ])
