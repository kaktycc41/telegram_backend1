from telethon import TelegramClient
import asyncio
import random

API_ID = 27877995
API_HASH = "f69a4c454706d10fea9f0e99cc91b353"
SESSION_NAME = "session_1"

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


async def auto_change_nick(nicknames, interval_minutes):
    """
    Har interval_minutes daqiqada bir marta random nickname tanlab, Telegram profilinga qo‘yadi.
    """
    print("✅ Nik o‘zgartirish jarayoni boshlandi...")
    async with client:
        while True:
            try:
                new_nick = random.choice(nicknames)
                await client(functions.account.UpdateProfileRequest(first_name=new_nick))
                print(f"🌀 Nik o‘zgardi: {new_nick}")
            except Exception as e:
                print(f"⚠️ Xatolik yuz berdi: {e}")
            await asyncio.sleep(interval_minutes * 60)
